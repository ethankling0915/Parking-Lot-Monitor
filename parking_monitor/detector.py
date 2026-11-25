"""Thin wrapper around an Ultralytics YOLO model.

Returns class names rather than IDs, so the code doesn't depend on the
class order Roboflow assigned during export.
"""
from ultralytics import YOLO


class Detector:
    def __init__(self, model_path, imgsz, conf):
        self.model = YOLO(model_path)
        self.imgsz = imgsz
        self.conf = conf

    def detect(self, frame):
        """Return a list of (class_name, x1, y1, x2, y2) for the frame."""
        result = self.model.predict(frame, imgsz=self.imgsz, conf=self.conf, verbose=False)[0]
        names = result.names
        detections = []
        for (x1, y1, x2, y2), cls_id in zip(result.boxes.xyxy.tolist(), result.boxes.cls.tolist()):
            detections.append((names[int(cls_id)], x1, y1, x2, y2))
        return detections