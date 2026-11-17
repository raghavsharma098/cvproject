"""
Module 1 - Real-time Face Detection (Viola-Jones Haar Cascade).

Usage:
    python detect_faces.py                 # webcam
    python detect_faces.py --eyes          # also detect eyes inside each face
    python detect_faces.py --image a.jpg   # detect on a still image

Keys: q = quit, s = save screenshot
"""
import argparse
import os
import time
import cv2

import config
from utils import ensure_dirs, load_cascade, open_camera, detect_faces, draw_box, put_info, FPSCounter


def annotate(frame, face_det, eye_det=None):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = detect_faces(face_det, gray)
    for i, (x, y, w, h) in enumerate(faces, 1):
        draw_box(frame, (x, y, w, h), f"Face {i}")
        if eye_det is not None:
            roi = gray[y:y + h // 2 + h // 6, x:x + w]   # eyes are in upper half
            for (ex, ey, ew, eh) in eye_det.detectMultiScale(roi, 1.1, 8, minSize=(15, 15)):
                cv2.rectangle(frame, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (255, 0, 0), 2)
    return frame, len(faces)


def run_image(path, face_det, eye_det):
    img = cv2.imread(path)
    if img is None:
        raise RuntimeError(f"Cannot read image {path}")
    img, n = annotate(img, face_det, eye_det)
    out = os.path.splitext(path)[0] + "_detected.jpg"
    cv2.imwrite(out, img)
    print(f"[INFO] {n} face(s) detected. Output saved to {out}")
    cv2.imshow("Face Detection", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def run_webcam(camera, face_det, eye_det):
    cap = open_camera(camera)
    fps = FPSCounter()
    print("[INFO] Press 'q' to quit, 's' to save a screenshot.")
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        frame, n = annotate(frame, face_det, eye_det)
        put_info(frame, [f"FPS: {fps.tick():.1f}", f"Faces: {n}"])
        cv2.imshow("Real-Time Face Detection", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("s"):
            p = os.path.join(config.SCREENSHOT_DIR, f"detect_{int(time.time())}.jpg")
            cv2.imwrite(p, frame)
            print(f"[INFO] Saved {p}")
    cap.release()
    cv2.destroyAllWindows()


def main():
    ap = argparse.ArgumentParser(description="Real-time face detection")
    ap.add_argument("--image", help="Run on a still image instead of webcam")
    ap.add_argument("--eyes", action="store_true", help="Also detect eyes")
    ap.add_argument("--camera", type=int, default=config.CAMERA_INDEX)
    args = ap.parse_args()

    ensure_dirs()
    face_det = load_cascade(config.FACE_CASCADE_PATH)
    eye_det = load_cascade(config.EYE_CASCADE_PATH) if args.eyes else None

    if args.image:
        run_image(args.image, face_det, eye_det)
    else:
        run_webcam(args.camera, face_det, eye_det)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        raise SystemExit(f"[ERROR] {e}")
