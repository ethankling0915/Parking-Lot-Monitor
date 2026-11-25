"""Click the corners of each parking spot on a video frame and save zone coordinates
in the video's full resolution.

Usage:
    python scripts/pick_zones.py data/raw/day1.mp4 600

The number is seconds into the video. Pick a moment with cars parked in the spots.

Controls:
    left click    add a corner (4 per spot; the spot is saved automatically)
    right click   remove the last corner you placed
    u             delete the last saved spot
    s             save to data/zones.yaml
    q             quit
"""
import sys
from pathlib import Path

import cv2
import numpy as np
import yaml

video = Path(sys.argv[1])
seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 600.0
DISPLAY_WIDTH = 1280  # the picture is shown at this width; clicks are scaled to full resolution

cap = cv2.VideoCapture(str(video))
cap.set(cv2.CAP_PROP_POS_MSEC, seconds * 1000)
ok, frame = cap.read()
cap.release()
if not ok:
    sys.exit("could not read a frame; try a different time")

full_h, full_w = frame.shape[:2]
scale = full_w / DISPLAY_WIDTH
display = cv2.resize(frame, (DISPLAY_WIDTH, round(full_h / scale)))
print(f"video frame: {full_w}x{full_h}. Saved coordinates use these pixels.")

zones = {}    # name -> corners in display coordinates
current = []  # corners of the spot being drawn, in display coordinates


def to_full_res(pts):
    return [[round(x * scale), round(y * scale)] for x, y in pts]


def zones_full_res():
    return {"zones": {name: to_full_res(pts) for name, pts in zones.items()}}


def on_mouse(event, x, y, flags, param):
    global current
    if event == cv2.EVENT_LBUTTONDOWN and len(current) < 4:
        current.append([int(x), int(y)])
        if len(current) == 4:
            zones[f"spot_{len(zones) + 1}"] = current
            current = []
    elif event == cv2.EVENT_RBUTTONDOWN and current:
        current.pop()


def redraw():
    canvas = display.copy()
    for name, pts in zones.items():
        arr = np.array(pts, dtype=np.int32)
        cv2.polylines(canvas, [arr], True, (0, 255, 0), 2)
        cv2.putText(canvas, name, tuple(int(v) for v in arr[0]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    if current:
        arr = np.array(current, dtype=np.int32)
        cv2.polylines(canvas, [arr], False, (0, 255, 255), 2)
        for x, y in current:
            cv2.circle(canvas, (x, y), 4, (0, 255, 255), -1)
    cv2.putText(canvas, "click 4 corners | right-click undo | u delete | s save | q quit",
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return canvas


cv2.namedWindow("zones", cv2.WINDOW_AUTOSIZE)
cv2.setMouseCallback("zones", on_mouse)
while True:
    cv2.imshow("zones", redraw())
    key = cv2.waitKey(20) & 0xFF
    if key == ord("q"):
        break
    if key == ord("u") and zones:
        zones.pop(list(zones)[-1])
    if key == ord("s"):
        out = Path("data/zones.yaml")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(yaml.safe_dump(zones_full_res(), sort_keys=False))
        print(f"saved {out}")

cv2.destroyAllWindows()
print(yaml.safe_dump(zones_full_res(), sort_keys=False))