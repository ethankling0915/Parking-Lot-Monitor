"""Write YOLO label files using the stock YOLO26 model.
Cars, trucks, buses, and motorcycles become class 0 (vehicle). People become class 2.
Your own car is not identified here. You relabel it during review.
Usage: python scripts/prelabel.py <frames_dir> <labels_dir> [weights]
"""
import sys
from pathlib import Path

from ultralytics import YOLO

frames_dir, labels_dir = Path(sys.argv[1]), Path(sys.argv[2])
weights = sys.argv[3] if len(sys.argv) > 3 else "yolo26n.pt"
labels_dir.mkdir(parents=True, exist_ok=True)

VEHICLE = {"car", "truck", "bus", "motorcycle"}
PERSON = {"person"}
TARGET_ID = {"vehicle": 0, "person": 2}

model = YOLO(weights)
images = sorted(frames_dir.glob("*.jpg"))
for start in range(0, len(images), 32):
    batch = images[start:start + 32]
    results = model.predict([str(p) for p in batch], imgsz=960, conf=0.25, verbose=False)
    for img_path, res in zip(batch, results):
        lines = []
        for (cx, cy, w, h), cls_id in zip(res.boxes.xywhn.tolist(), res.boxes.cls.tolist()):
            name = res.names[int(cls_id)]
            if name in VEHICLE:
                out_id = TARGET_ID["vehicle"]
            elif name in PERSON:
                out_id = TARGET_ID["person"]
            else:
                continue
            lines.append(f"{out_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
        (labels_dir / (img_path.stem + ".txt")).write_text("\n".join(lines))
print(f"wrote {len(images)} label files to {labels_dir}")