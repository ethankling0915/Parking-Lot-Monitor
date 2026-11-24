"""Build a TensorRT engine. Run on the Jetson only.

TensorRT engines only run on the device and TensorRT version that built them,
so build the engine on the Jetson and never copy one from another machine.

Usage:
    python scripts/export_tensorrt.py yolo26n.pt 960
"""
import sys

from ultralytics import YOLO

weights = sys.argv[1] if len(sys.argv) > 1 else "yolo26n.pt"
imgsz = int(sys.argv[2]) if len(sys.argv) > 2 else 960

model = YOLO(weights)
model.export(format="engine", half=True, imgsz=imgsz)
print(f"exported {weights} at imgsz={imgsz}. Set model and imgsz in config.yaml to match.")
