"""Save one frame every N seconds from a video.
Usage: python scripts/extract_frames.py <video> <out_dir> [seconds_between_frames]
"""
import sys
from pathlib import Path

import cv2

video, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
step_s = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0
out_dir.mkdir(parents=True, exist_ok=True)

cap = cv2.VideoCapture(str(video))
every = max(1, int(round((cap.get(cv2.CAP_PROP_FPS) or 30.0) * step_s)))
frame_no, saved = 0, 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    if frame_no % every == 0:
        cv2.imwrite(str(out_dir / f"{video.stem}_{frame_no:07d}.jpg"), frame)
        saved += 1
    frame_no += 1
cap.release()
print(f"{video.name}: saved {saved} frames")