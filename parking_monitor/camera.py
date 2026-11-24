"""Open the webcam or a recorded clip the same way on Windows and Linux."""
import platform

import cv2


def is_live(source):
    """True for a camera index, False for a file path."""
    return str(source).isdigit()


def open_source(source, width, height):
    if is_live(source):
        index = int(source)
        # DirectShow on Windows, V4L2 on Linux (the Jetson).
        backend = cv2.CAP_DSHOW if platform.system() == "Windows" else cv2.CAP_V4L2
        cap = cv2.VideoCapture(index, backend)
        # MJPG keeps USB bandwidth low enough for 1080p.
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    else:
        cap = cv2.VideoCapture(str(source))
    if not cap.isOpened():
        raise RuntimeError(f"could not open source {source!r}")
    return cap
