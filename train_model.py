"""
Module 3 - Model Training (LBPH: Local Binary Pattern Histograms).
Reads dataset/<person>/*.jpg, assigns an integer ID to each person,
trains an LBPH recogniser and saves the model + label map.

Usage:
    python train_model.py            # train on all images
    python train_model.py --eval     # also report accuracy on an 80/20 split
"""
import argparse
import json
import os
import random
import sys
import time
import cv2
import numpy as np

import config
from utils import ensure_dirs, preprocess_face


def create_recognizer():
    if not hasattr(cv2, "face"):
        raise RuntimeError("cv2.face not found. Install: pip install opencv-contrib-python "
                           "(uninstall plain opencv-python first)")
    return cv2.face.LBPHFaceRecognizer_create(
        radius=config.LBPH_RADIUS,
        neighbors=config.LBPH_NEIGHBORS,
        grid_x=config.LBPH_GRID_X,
        grid_y=config.LBPH_GRID_Y,
    )


def list_people():
    if not os.path.isdir(config.DATASET_DIR):
        return []
    return sorted(d for d in os.listdir(config.DATASET_DIR)
                  if os.path.isdir(os.path.join(config.DATASET_DIR, d)))


def image_files(person):
    folder = os.path.join(config.DATASET_DIR, person)
    if not os.path.isdir(folder):
        return []
    return sorted((f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))),
                  key=lambda f: (len(f), f))


def load_dataset(log=print):
    faces, ids, label_map, counts = [], [], {}, []
    pid = 0
    for person in list_people():
        n = 0
        for f in image_files(person):
            img = cv2.imread(os.path.join(config.DATASET_DIR, person, f), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            faces.append(preprocess_face(img))
            ids.append(pid)
            n += 1
        if n == 0:
            log(f"  [skip] {person:<20} no images")
            continue
        label_map[pid] = person
        counts.append({"id": pid, "name": person, "images": n})
        log(f"  [{pid}] {person:<20} {n} images")
        pid += 1
    return faces, np.array(ids, dtype=np.int32), label_map, counts


def evaluate(faces, ids, test_ratio=0.2, seed=42, log=print):
    idx = list(range(len(faces)))
    random.Random(seed).shuffle(idx)
    split = int(len(idx) * (1 - test_ratio))
    tr, te = idx[:split], idx[split:]
    if not tr or not te:
        log("[EVAL] Not enough images for an evaluation split.")
        return None
    rec = create_recognizer()
    rec.train([faces[i] for i in tr], ids[tr])
    correct, unknown = 0, 0
    for i in te:
        pred, dist = rec.predict(faces[i])
        if dist > config.CONFIDENCE_THRESHOLD:
            unknown += 1
        elif pred == ids[i]:
            correct += 1
    acc = 100 * correct / len(te)
    log(f"[EVAL] Test samples: {len(te)} | Correct: {correct} | "
        f"Rejected as Unknown: {unknown} | Accuracy: {acc:.2f}%")
    return {"test": len(te), "correct": correct, "unknown": unknown,
            "wrong": len(te) - correct - unknown, "accuracy": round(acc, 2)}


def train(do_eval=False, log=print):
    """Train on the whole dataset and save the model. Returns a summary dict."""
    ensure_dirs()
    t0 = time.time()
    log("[INFO] Loading dataset...")
    faces, ids, label_map, counts = load_dataset(log)
    if not label_map:
        raise RuntimeError("Dataset is empty. Register at least one person first.")

    evaluation = evaluate(faces, ids, log=log) if do_eval else None

    log("[INFO] Training LBPH model on all samples...")
    rec = create_recognizer()
    rec.train(faces, ids)
    tmp = os.path.join(config.MODEL_DIR, "lbph_model.tmp.yml")
    rec.write(tmp)
    os.replace(tmp, config.MODEL_PATH)       # atomic: live recognition never reads half a file
    with open(config.LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(label_map, f, indent=2)
    secs = time.time() - t0
    log(f"[DONE] {len(label_map)} person(s), {len(faces)} images in {secs:.1f}s")
    return {"people": counts, "images": len(faces), "evaluation": evaluation, "seconds": round(secs, 2)}


def main():
    ap = argparse.ArgumentParser(description="Train LBPH face recogniser")
    ap.add_argument("--eval", action="store_true", help="Report hold-out accuracy")
    args = ap.parse_args()
    train(args.eval)
    print(f"       Model  -> {config.MODEL_PATH}")
    print(f"       Labels -> {config.LABELS_PATH}")
    print("[NEXT] Run: python recognize_faces.py")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        sys.exit(f"[ERROR] {e}")
