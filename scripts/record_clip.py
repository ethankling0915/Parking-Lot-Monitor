"""Record webcam footage to a clip for offline testing.

Usage:
    python scripts/record_clip.py [camera_index] [minutes]
    python scripts/record_clip.py 0 10
"""
import sys
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from parking_monitor.camera import open_source  # noqa: E402


def main():
    index = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    minutes = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0

    cap = open_source(index, 1920, 1080)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out_dir = Path("clips")
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"clip_{time.strftime('%Y%m%d_%H%M%S')}.mp4"
    writer = cv2.VideoWriter(str(out), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

    end = time.time() + minutes * 60
    frames = 0
    while time.time() < end:
        ok, frame = cap.read()
        if ok:
            writer.write(frame)
            frames += 1

    cap.release()
    writer.release()
    print(f"wrote {out} ({frames} frames at {fps:.0f} fps)")


if __name__ == "__main__":
    main()
