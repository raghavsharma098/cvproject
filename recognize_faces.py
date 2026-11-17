"""
Module 4 - Real-time Face Recognition (+ optional attendance logging).

Usage:
    python recognize_faces.py
    python recognize_faces.py --attendance          # mark attendance in CSV
    python recognize_faces.py --threshold 60        # stricter matching
    python recognize_faces.py --image group.jpg     # recognise in a still image

Keys: q = quit, s = save screenshot
"""
import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime
import cv2

import config
from utils import (ensure_dirs, load_cascade, open_camera, detect_faces,
                   preprocess_face, draw_box, put_info, FPSCounter)
from train_model import create_recognizer

KNOWN_COLOR = (90, 220, 80)
UNKNOWN_COLOR = (70, 70, 240)


def load_model():
    if not (os.path.exists(config.MODEL_PATH) and os.path.exists(config.LABELS_PATH)):
        raise RuntimeError("Model not found. Register people and train the model first.")
    rec = create_recognizer()
    rec.read(config.MODEL_PATH)
    with open(config.LABELS_PATH, encoding="utf-8") as f:
        labels = {int(k): v for k, v in json.load(f).items()}
    return rec, labels


def attendance_path(date):
    return os.path.join(config.ATTENDANCE_DIR, f"attendance_{date}.csv")


class Attendance:
    """Writes each recognised person once per day to attendance/attendance_<date>.csv"""

    def __init__(self):
        self.date = None
        self._open_today()

    def _open_today(self):
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.path = attendance_path(self.date)
        self.marked = set()
        if os.path.exists(self.path):
            with open(self.path, encoding="utf-8") as f:
                self.marked = {row["Name"] for row in csv.DictReader(f)}
        else:
            with open(self.path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["Name", "Date", "Time", "Match %"])

    def mark(self, name, score):
        if datetime.now().strftime("%Y-%m-%d") != self.date:   # new day -> new file
            self._open_today()
        if name in self.marked:
            return False
        now = datetime.now()
        with open(self.path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([name, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), f"{score:.1f}"])
        self.marked.add(name)
        print(f"[ATTENDANCE] {name} marked present at {now.strftime('%H:%M:%S')}")
        return True


def recognise_frame(frame, detector, rec, labels, threshold, attendance=None):
    """Annotate frame in place. Returns (frame, results) where results is a list of dicts."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detect_faces(detector, gray)
    results = []
    for (x, y, w, h) in faces:
        face = preprocess_face(gray[y:y + h, x:x + w])
        pid, dist = rec.predict(face)
        # convert LBPH distance to an intuitive 0-100 "match %"
        score = max(0.0, 100.0 - dist)
        known = dist <= threshold and pid in labels
        name = labels[pid] if known else "Unknown"
        marked = bool(attendance.mark(name, score)) if (known and attendance) else False
        results.append({"name": name, "known": known, "score": round(score, 1),
                        "distance": round(float(dist), 1), "marked": marked,
                        "box": [int(x), int(y), int(w), int(h)]})
        draw_box(frame, (x, y, w, h), f"{name} {score:.0f}%", KNOWN_COLOR if known else UNKNOWN_COLOR)
    return frame, results


def main():
    ap = argparse.ArgumentParser(description="Real-time face recognition")
    ap.add_argument("--camera", type=int, default=config.CAMERA_INDEX)
    ap.add_argument("--threshold", type=float, default=config.CONFIDENCE_THRESHOLD,
                    help="Max LBPH distance to accept a match (lower = stricter)")
    ap.add_argument("--attendance", action="store_true", help="Log recognised people to CSV")
    ap.add_argument("--image", help="Recognise faces in a still image")
    args = ap.parse_args()

    ensure_dirs()
    detector = load_cascade(config.FACE_CASCADE_PATH)
    rec, labels = load_model()
    print(f"[INFO] Loaded model with {len(labels)} person(s): {', '.join(labels.values())}")
    attendance = Attendance() if args.attendance else None

    if args.image:
        img = cv2.imread(args.image)
        if img is None:
            raise RuntimeError(f"Cannot read {args.image}")
        img, results = recognise_frame(img, detector, rec, labels, args.threshold, attendance)
        out = os.path.splitext(args.image)[0] + "_recognized.jpg"
        cv2.imwrite(out, img)
        print(f"[INFO] Found: {[r['name'] for r in results]}. Saved {out}")
        cv2.imshow("Face Recognition", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    cap = open_camera(args.camera)
    fps = FPSCounter()
    print("[INFO] Press 'q' to quit, 's' to save screenshot.")
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        frame, results = recognise_frame(frame, detector, rec, labels, args.threshold, attendance)
        info = [f"FPS: {fps.tick():.1f}", f"Faces: {len(results)}"]
        if attendance:
            info.append(f"Present: {len(attendance.marked)}")
        put_info(frame, info)
        cv2.imshow("Real-Time Face Recognition", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("s"):
            p = os.path.join(config.SCREENSHOT_DIR, f"recognize_{int(time.time())}.jpg")
            cv2.imwrite(p, frame)
            print(f"[INFO] Saved {p}")
    cap.release()
    cv2.destroyAllWindows()
    if attendance:
        print(f"[INFO] Attendance file: {attendance.path}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        sys.exit(f"[ERROR] {e}")
