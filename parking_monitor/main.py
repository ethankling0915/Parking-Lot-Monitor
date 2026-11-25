"""Run the parking monitor: read frames, detect vehicles, log zone changes and visits.

Examples:
    python -m parking_monitor.main --config config/config.yaml
    python -m parking_monitor.main --source data/raw/day2.mp4 --db data/test.db --ignore-window --show
"""
import argparse
import datetime as dt
import time
from pathlib import Path

import cv2
import yaml

from parking_monitor.camera import is_live, open_source
from parking_monitor.detector import Detector
from parking_monitor.events import EventLog
from parking_monitor.occupancy import ZoneState
from parking_monitor.zones import Zone, occupied_zone_names

PAUSE_FILE = Path("data/PAUSE")


def in_window(start, end, now=None):
    """True if the current local time is between start and end ("HH:MM")."""
    now_t = (now or dt.datetime.now()).time()
    return dt.time.fromisoformat(start) <= now_t < dt.time.fromisoformat(end)


def parse_args():
    p = argparse.ArgumentParser(description="Parking lot monitor")
    p.add_argument("--config", default="config/config.yaml")
    p.add_argument("--source", help="camera index or clip path; overrides the config")
    p.add_argument("--db", help="event database path; overrides the config")
    p.add_argument("--ignore-window", action="store_true",
                   help="run even outside the daytime window")
    p.add_argument("--show", action="store_true",
                   help="show zones and detections (needs a display)")
    return p.parse_args()


def draw(frame, zones, detections, occupied):
    for zone in zones:
        color = (0, 0, 255) if zone.name in occupied else (0, 255, 0)
        cv2.polylines(frame, [zone.polygon.reshape(-1, 1, 2)], True, color, 2)
        label_at = tuple(int(v) for v in zone.polygon[0])
        cv2.putText(frame, zone.name, label_at, cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    for name, x1, y1, x2, y2 in detections:
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 0), 1)
        cv2.putText(frame, name, (int(x1), int(y1) - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)


def main():
    args = parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text())

    source = cfg["source"] if args.source is None else args.source
    live = is_live(source)
    db_path = args.db or cfg["db_path"]
    width, height = cfg["frame_width"], cfg["frame_height"]
    counted = set(cfg["counted_classes"])
    visit_zone_name = cfg.get("visit_zone", "parking_area")

    if visit_zone_name not in cfg["zones"]:
        raise SystemExit(f"config zones must include '{visit_zone_name}' "
                         f"(one large zone covering the area between the trees)")

    zones = [Zone(name, pts) for name, pts in cfg["zones"].items()]
    visit_zone = next(z for z in zones if z.name == visit_zone_name)
    states = {z.name: ZoneState(z.name, cfg["debounce_seconds"]) for z in zones}
    visit_state = ZoneState(visit_zone_name, cfg["debounce_seconds"])

    detector = Detector(cfg["model"], cfg["imgsz"], cfg["conf"])
    log = EventLog(db_path)
    log.log("start", detail=f"source={source}")

    cap = None
    frame_no = 0
    while True:
        # Pause and daytime window apply to the live camera only. Replays always run.
        active = not PAUSE_FILE.exists() and (
            not live or args.ignore_window
            or in_window(cfg["window"]["start"], cfg["window"]["end"])
        )
        if not active:
            # Release the camera so other programs (like drone work) can use it.
            if cap is not None:
                cap.release()
                cap = None
            time.sleep(30)
            continue

        if cap is None:
            cap = open_source(source, width, height)

        ok, frame = cap.read()
        if not ok:
            if not live:
                break  # end of clip
            log.log("camera_error")
            cap.release()
            cap = None
            time.sleep(5)
            continue

        frame_no += 1
        if frame_no % cfg["process_every_n_frames"]:
            continue

        # Live frames use wall-clock time. Clips use video time so replays
        # behave the same whether they play fast or slow.
        ts = time.time() if live else cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

        detections = detector.detect(frame)

        # Spot occupancy: any counted vehicle (including your car) in a zone.
        boxes = [(x1, y1, x2, y2) for name, x1, y1, x2, y2 in detections if name in counted]
        occupied = occupied_zone_names(boxes, zones)
        for zone in zones:
            change = states[zone.name].update(ts, zone.name in occupied)
            if change:
                log.log(change, zone=zone.name, ts=ts)
                print(f"{zone.name}: {change}")

        # Visits: your car (my_car only) inside the parking area.
        my_car_boxes = [(x1, y1, x2, y2) for name, x1, y1, x2, y2 in detections
                        if name == "my_car"]
        my_car_in_area = visit_zone_name in occupied_zone_names(my_car_boxes, [visit_zone])
        change = visit_state.update(ts, my_car_in_area)
        if change:
            kind = "my_car_arrived" if change == "occupied" else "my_car_left"
            log.log(kind, zone=visit_zone_name, ts=ts)
            print(f"{kind} in {visit_zone_name}")

        if args.show:
            draw(frame, zones, detections, occupied)
            cv2.imshow("parking-lot-monitor", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    if cap is not None:
        cap.release()
    log.log("stop")
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()