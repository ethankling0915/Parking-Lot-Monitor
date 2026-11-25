"""Build a YOLO dataset. Frames from the validation video go to val; everything else goes to train.
Usage: python scripts/make_dataset.py <frames_dir> <labels_dir> <out_dir> <val_video_stem>
Example: python scripts/make_dataset.py data/frames data/prelabels data/dataset day2
"""
import shutil
import sys
from pathlib import Path

frames_dir, labels_dir, out_dir = (Path(p) for p in sys.argv[1:4])
val_stem = sys.argv[4]

for split in ("train", "val"):
    (out_dir / "images" / split).mkdir(parents=True, exist_ok=True)
    (out_dir / "labels" / split).mkdir(parents=True, exist_ok=True)

counts = {"train": 0, "val": 0}
for img in sorted(frames_dir.glob("*.jpg")):
    split = "val" if img.stem.startswith(val_stem) else "train"
    shutil.copy2(img, out_dir / "images" / split / img.name)
    label = labels_dir / (img.stem + ".txt")
    dest = out_dir / "labels" / split / (img.stem + ".txt")
    if label.exists():
        shutil.copy2(label, dest)
    else:
        dest.write_text("")  # an image with no objects still needs an empty label file
    counts[split] += 1

(out_dir / "data.yaml").write_text(
    f"path: {out_dir.resolve().as_posix()}\n"
    "train: images/train\n"
    "val: images/val\n"
    "names:\n"
    "  0: vehicle\n"
    "  1: my_car\n"
    "  2: person\n"
)
print(counts)