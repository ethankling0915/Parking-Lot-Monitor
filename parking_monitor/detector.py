"""Thin wrapper around an Ultralytics YOLO model."""
from ultralytics import YOLO


class Detector:
    def __init__(self, model_path, imgsz, conf, classes=None):
        self.model = YOLO(model_path)
        self.imgsz = imgsz
        self.conf = conf
        self.classes = classes

    def detect(self, frame):
        """Return a list of (x1, y1, x2, y2) boxes found in the frame."""
        result = self.model.predict(
            frame,
            imgsz=self.imgsz,
            conf=self.conf,
            classes=self.classes,
            verbose=False,
        )[0]
        return [tuple(box) for box in result.boxes.xyxy.tolist()]
