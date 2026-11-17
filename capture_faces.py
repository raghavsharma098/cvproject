"""
Module 2 - Dataset Collection.
Captures face samples of one person from the webcam and stores them as
dataset/<name>/<n>.jpg (grayscale, 200x200, histogram-equalised).

Usage:
    python capture_faces.py --name Raghav
    python capture_faces.py --name Palak --samples 80

Tips: move your head slightly (left/right/up/down), change expression,
and vary distance so the model sees different poses.
Keys: q = stop early
"""
import argparse
import os
import time
import cv2

import config
from utils import clean_name, next_sample_index, ensure_dirs, load_cascade, open_camera, detect_faces, preprocess_face, draw_box, put_info


def main():
    ap = argparse.ArgumentParser(description="Capture face samples for one person")
    ap.add_argument("--name", required=True, help="Person's name (folder name)")
    ap.add_argument("--samples", type=int, default=config.SAMPLES_PER_PERSON)
    ap.add_argument("--camera", type=int, default=config.CAMERA_INDEX)
    ap.add_argument("--delay", type=float, default=config.SAMPLE_DELAY, help="Seconds between saved samples")
    args = ap.parse_args()

    ensure_dirs()
    name = clean_name(args.name)
    if not name:
        raise RuntimeError("Invalid name. Use letters, digits, _ or -")
    person_dir = os.path.join(config.DATASET_DIR, name)
    os.makedirs(person_dir, exist_ok=True)
    start_idx = next_sample_index(person_dir) - 1

    detector = load_cascade(config.FACE_CASCADE_PATH)
    cap = open_camera(args.camera)
    count, last_save = 0, 0.0
    print(f"[INFO] Capturing {args.samples} samples for '{name}'. Look at the camera...")

    while count < args.samples:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detect_faces(detector, gray)

        status = "Saving..."
        color = (0, 255, 0)
        if len(faces) == 0:
            status, color = "No face detected", (0, 0, 255)
        elif len(faces) > 1:
            status, color = "Only ONE person please", (0, 0, 255)
        else:
            x, y, w, h = faces[0]
            draw_box(frame, (x, y, w, h), name, color)
            if time.time() - last_save >= args.delay:
                face = preprocess_face(gray[y:y + h, x:x + w])
                cv2.imwrite(os.path.join(person_dir, f"{start_idx + count + 1}.jpg"), face)
                count += 1
                last_save = time.time()

        # progress bar
        bar_w = int((count / args.samples) * (frame.shape[1] - 20))
        cv2.rectangle(frame, (10, frame.shape[0] - 25), (10 + bar_w, frame.shape[0] - 10), (0, 255, 0), -1)
        put_info(frame, [f"Samples: {count}/{args.samples}", status])
        cv2.imshow("Dataset Capture", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"[DONE] Saved {count} images to {person_dir}")
    print("[NEXT] Run: python train_model.py")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        raise SystemExit(f"[ERROR] {e}")
