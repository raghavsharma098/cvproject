"""Shared helpers: detector loading, preprocessing, drawing and FPS measurement.

Helpers raise RuntimeError on failure (instead of exiting) so they can be used
both by the command-line scripts and by the web dashboard.
"""
import os
import re
import sys
import time
import cv2

import config


def ensure_dirs():
    for d in (config.DATASET_DIR, config.MODEL_DIR, config.ATTENDANCE_DIR,
              config.SCREENSHOT_DIR, config.UPLOAD_DIR):
        os.makedirs(d, exist_ok=True)


def clean_name(name):
    """Make a person's name safe to use as a folder name."""
    name = re.sub(r"\s+", "_", (name or "").strip())
    return re.sub(r"[^A-Za-z0-9_\-]", "", name)[:40]


def load_cascade(path):
    cascade = cv2.CascadeClassifier(path)
    if cascade.empty():
        raise RuntimeError(f"Could not load Haar cascade: {path}")
    return cascade


def open_camera(index=config.CAMERA_INDEX):
    """Open a webcam. On Windows DirectShow opens much faster than the default backend."""
    backends = [cv2.CAP_DSHOW, cv2.CAP_ANY] if sys.platform.startswith("win") else [cv2.CAP_ANY]
    for backend in backends:
        cap = cv2.VideoCapture(index, backend)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
            ok, _ = cap.read()
            if ok:
                return cap
        cap.release()
    raise RuntimeError(f"Cannot open camera index {index}. Check that no other app is using "
                       f"the webcam, or try another camera index.")


def detect_faces(detector, gray):
    """Return list of (x, y, w, h) boxes using Viola-Jones Haar cascade."""
    return detector.detectMultiScale(
        gray,
        scaleFactor=config.SCALE_FACTOR,
        minNeighbors=config.MIN_NEIGHBORS,
        minSize=config.MIN_FACE_SIZE,
    )


def preprocess_face(gray_face):
    """Resize to a fixed size and equalise histogram (reduces lighting effects)."""
    face = cv2.resize(gray_face, config.FACE_SIZE)
    return cv2.equalizeHist(face)


def draw_box(frame, box, label, color=(0, 220, 120)):
    x, y, w, h = [int(v) for v in box]
    # corner-style box
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 1)
    L = max(12, w // 5)
    for (cx, cy, dx, dy) in ((x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
        cv2.line(frame, (cx, cy), (cx + dx * L, cy), color, 3)
        cv2.line(frame, (cx, cy), (cx, cy + dy * L), color, 3)
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
    ty = y - 8 if y - th - 14 > 0 else y + h + th + 12
    cv2.rectangle(frame, (x, ty - th - 6), (x + tw + 10, ty + 5), color, -1)
    cv2.putText(frame, label, (x + 5, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 1, cv2.LINE_AA)


def put_info(frame, lines, origin=(10, 25)):
    x, y = origin
    for line in lines:
        cv2.putText(frame, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(frame, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1, cv2.LINE_AA)
        y += 24


class FPSCounter:
    """Smoothed frames-per-second counter."""

    def __init__(self, alpha=0.9):
        self.alpha = alpha
        self.prev = time.time()
        self.fps = 0.0

    def tick(self):
        now = time.time()
        inst = 1.0 / max(now - self.prev, 1e-6)
        self.prev = now
        self.fps = inst if self.fps == 0 else self.alpha * self.fps + (1 - self.alpha) * inst
        return self.fps


def next_sample_index(person_dir):
    """Next free numeric file name in a person's folder (so new samples never overwrite old ones)."""
    nums = [int(os.path.splitext(f)[0]) for f in os.listdir(person_dir)
            if os.path.splitext(f)[0].isdigit()] if os.path.isdir(person_dir) else []
    return max(nums, default=0) + 1
