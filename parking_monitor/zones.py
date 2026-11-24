"""Decide which parking zones contain a vehicle."""
import cv2
import numpy as np


class Zone:
    def __init__(self, name, polygon):
        self.name = name
        self.polygon = np.array(polygon, dtype=np.int32)

    def contains_point(self, x, y):
        return cv2.pointPolygonTest(self.polygon, (float(x), float(y)), False) >= 0


def occupied_zone_names(boxes, zones):
    """Names of zones that contain the bottom-center point of any box.

    The bottom-center is where a car touches the ground, so it is more
    reliable than the box center for deciding which spot a car is in.
    """
    names = set()
    for x1, y1, x2, y2 in boxes:
        foot_x, foot_y = (x1 + x2) / 2, y2
        for zone in zones:
            if zone.contains_point(foot_x, foot_y):
                names.add(zone.name)
    return names
