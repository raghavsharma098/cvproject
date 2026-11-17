"""
Camera engine for the web dashboard.

One background thread owns the webcam and processes frames according to the
current mode:
    detect     - Haar face (+ optional eye) detection
    recognize  - LBPH recognition (+ optional attendance)
    capture    - dataset collection for one person
The latest annotated JPEG is shared with any number of MJPEG stream clients.
"""
import csv
import os
import shutil
import threading
import time
from datetime import datetime

import cv2

import config
from utils import (ensure_dirs, load_cascade, open_camera, detect_faces, preprocess_face,
                   draw_box, FPSCounter, clean_name, next_sample_index)
from train_model import list_people, image_files, train as train_dataset
from recognize_faces import load_model, recognise_frame, Attendance, attendance_path

MODES = ("detect", "recognize", "capture")


class CameraService:
    def __init__(self):
        ensure_dirs()
        self.face_det = load_cascade(config.FACE_CASCADE_PATH)
        self.eye_det = load_cascade(config.EYE_CASCADE_PATH)

        self.lock = threading.RLock()
        self.cond = threading.Condition()
        self.stop_event = threading.Event()
        self.thread = None
        self.running = False

        self.mode = "idle"
        self.camera_index = config.CAMERA_INDEX
        self.opened_index = None
        self.eyes = False
        self.attendance_on = False
        self.threshold = config.CONFIDENCE_THRESHOLD

        self.jpeg = None
        self.frame = None
        self.frame_id = 0
        self.error = None
        self.last_viewed = 0.0
        self.fps = 0.0
        self.results = []
        self.capture = self._empty_capture()
        self.attendance = None
        self.recent_marks = []

        self.rec, self.labels, self.model_mtime = None, {}, None

    # ------------------------------------------------------------------ control
    @staticmethod
    def _empty_capture():
        return {"name": None, "target": 0, "count": 0, "status": "", "done": False,
                "dir": None, "next": 1, "last": 0.0}

    def start(self, mode, camera=None, eyes=None, attendance=None, threshold=None,
              name=None, samples=None):
        if mode not in MODES:
            raise ValueError(f"Unknown mode '{mode}'")
        with self.lock:
            if camera is not None:
                self.camera_index = int(camera)
            self.update_settings(eyes=eyes, attendance=attendance, threshold=threshold)
            if mode == "recognize":
                self._ensure_model()
                if self.attendance_on and self.attendance is None:
                    self.attendance = Attendance()
            if mode == "capture":
                person = clean_name(name)
                if not person:
                    raise ValueError("Please enter a valid name (letters, digits, _ or -).")
                folder = os.path.join(config.DATASET_DIR, person)
                os.makedirs(folder, exist_ok=True)
                cap = self._empty_capture()
                cap.update(name=person, dir=folder, next=next_sample_index(folder),
                           target=max(5, min(int(samples or config.SAMPLES_PER_PERSON), 300)),
                           status="Look at the camera")
                self.capture = cap
            self.mode = mode
            self.error = None
            self.last_viewed = time.time()
            restart = self.running and self.opened_index != self.camera_index
        if self.thread is not None and not self.thread.is_alive():
            self.running = False
        if restart:
            self._stop_thread()
            with self.lock:
                self.mode = mode       # the old thread resets mode to idle on exit
        if not self.running:
            self.running = True
            self.stop_event.clear()
            start_id = self.frame_id
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()
            # wait for the first frame (or an error) so the UI gets immediate feedback
            with self.cond:
                self.cond.wait_for(lambda: self.frame_id != start_id or not self.running, timeout=10)
            if self.error:
                raise RuntimeError(self.error)

    def update_settings(self, eyes=None, attendance=None, threshold=None):
        with self.lock:
            if eyes is not None:
                self.eyes = bool(eyes)
            if threshold is not None:
                self.threshold = max(10.0, min(float(threshold), 150.0))
            if attendance is not None:
                self.attendance_on = bool(attendance)
                if self.attendance_on and self.attendance is None:
                    self.attendance = Attendance()

    def stop(self):
        self._stop_thread()
        with self.lock:
            self.mode = "idle"

    def _stop_thread(self):
        self.stop_event.set()
        if self.thread and self.thread.is_alive() and self.thread is not threading.current_thread():
            self.thread.join(timeout=5)
        self.running = False

    # ------------------------------------------------------------------ model
    def _ensure_model(self):
        """(Re)load the LBPH model if it is missing or was retrained on disk."""
        mtime = os.path.getmtime(config.MODEL_PATH) if os.path.exists(config.MODEL_PATH) else None
        if mtime is None:
            raise RuntimeError("No trained model yet. Register people and train the model first.")
        if self.rec is None or mtime != self.model_mtime:
            self.rec, self.labels = load_model()
            self.model_mtime = mtime

    def train(self, do_eval=False):
        logs = []
        result = train_dataset(do_eval, log=logs.append)
        result["log"] = logs
        with self.lock:
            self.rec = None            # force reload on next recognition frame
        return result

    # ------------------------------------------------------------------ loop
    def _loop(self):
        try:
            cap = open_camera(self.camera_index)
            self.opened_index = self.camera_index
        except RuntimeError as e:
            with self.lock:
                self.error, self.mode = str(e), "idle"
            self.running = False
            with self.cond:
                self.cond.notify_all()
            return

        fps = FPSCounter()
        try:
            while not self.stop_event.is_set():
                if time.time() - self.last_viewed > config.CAMERA_IDLE_TIMEOUT:
                    break                                   # nobody is watching -> free the webcam
                ok, frame = cap.read()
                if not ok:
                    self.error = "Lost connection to the camera."
                    break
                frame = cv2.flip(frame, 1)
                with self.lock:
                    mode = self.mode
                    try:
                        if mode == "detect":
                            results = self._process_detect(frame)
                        elif mode == "recognize":
                            results = self._process_recognize(frame)
                        elif mode == "capture":
                            results = self._process_capture(frame)
                        else:
                            results = []
                    except Exception as e:                   # never kill the camera thread
                        results = []
                        self.error = str(e)
                    self.results = results
                    self.fps = fps.tick()
                ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 82])
                with self.cond:
                    self.frame, self.jpeg = frame, buf.tobytes()
                    self.frame_id += 1
                    self.cond.notify_all()
                if mode == "capture" and self.capture["done"]:
                    time.sleep(0.6)                          # let the UI show the final frame
                    break
        finally:
            cap.release()
            self.opened_index = None
            with self.lock:
                self.mode = "idle"
                self.results, self.fps = [], 0.0
            self.running = False
            with self.cond:
                self.jpeg = None
                self.cond.notify_all()

    def _process_detect(self, frame):
        gray = cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        faces = detect_faces(self.face_det, gray)
        results = []
        for i, (x, y, w, h) in enumerate(faces, 1):
            draw_box(frame, (x, y, w, h), f"Face {i}", (240, 180, 60))
            eyes = 0
            if self.eyes:
                roi = gray[y:y + h // 2 + h // 6, x:x + w]
                for (ex, ey, ew, eh) in self.eye_det.detectMultiScale(roi, 1.1, 8, minSize=(15, 15)):
                    cv2.ellipse(frame, (x + ex + ew // 2, y + ey + eh // 2), (ew // 2, eh // 2),
                                0, 0, 360, (255, 120, 200), 2)
                    eyes += 1
            results.append({"name": f"Face {i}", "known": None, "eyes": eyes,
                            "box": [int(x), int(y), int(w), int(h)]})
        return results

    def _process_recognize(self, frame):
        self._ensure_model()
        att = self.attendance if self.attendance_on else None
        _, results = recognise_frame(frame, self.face_det, self.rec, self.labels, self.threshold, att)
        now = datetime.now().strftime("%H:%M:%S")
        for r in results:
            if r["marked"]:
                self.recent_marks.insert(0, {"name": r["name"], "time": now, "score": r["score"]})
                del self.recent_marks[20:]
        return results

    def _process_capture(self, frame):
        c = self.capture
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detect_faces(self.face_det, gray)
        if c["done"]:
            pass
        elif len(faces) == 0:
            c["status"] = "No face detected - look at the camera"
        elif len(faces) > 1:
            c["status"] = "Only ONE person in front of the camera please"
            for b in faces:
                draw_box(frame, b, "?", (70, 70, 240))
        else:
            x, y, w, h = faces[0]
            draw_box(frame, (x, y, w, h), c["name"], (90, 220, 80))
            c["status"] = "Capturing... slowly turn your head and change expression"
            if time.time() - c["last"] >= config.SAMPLE_DELAY:
                face = preprocess_face(gray[y:y + h, x:x + w])
                cv2.imwrite(os.path.join(c["dir"], f"{c['next']}.jpg"), face)
                c["next"] += 1
                c["count"] += 1
                c["last"] = time.time()
                if c["count"] >= c["target"]:
                    c["done"], c["status"] = True, "Done! Now train the model."
        # progress bar along the bottom of the frame
        H, W = frame.shape[:2]
        cv2.rectangle(frame, (0, H - 8), (W, H), (40, 40, 40), -1)
        cv2.rectangle(frame, (0, H - 8), (int(W * c["count"] / max(c["target"], 1)), H), (90, 220, 80), -1)
        return [{"name": c["name"], "known": True, "box": [int(v) for v in b]} for b in faces]

    # ------------------------------------------------------------------ outputs
    def mjpeg(self):
        """Generator for a multipart MJPEG stream."""
        last = -1
        while True:
            with self.cond:
                self.cond.wait_for(lambda: self.frame_id != last or not self.running, timeout=2)
                if not self.running:
                    return
                data, last = self.jpeg, self.frame_id
            self.last_viewed = time.time()
            if data:
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + data + b"\r\n"

    def screenshot(self):
        with self.cond:
            frame = None if self.frame is None or not self.running else self.frame.copy()
        if frame is None:
            raise RuntimeError("Camera is not running.")
        name = f"{self.mode}_{datetime.now():%Y%m%d_%H%M%S}.jpg"
        cv2.imwrite(os.path.join(config.SCREENSHOT_DIR, name), frame)
        return name

    def status(self):
        with self.lock:
            c = self.capture
            return {
                "running": self.running, "mode": self.mode, "camera": self.camera_index,
                "eyes": self.eyes, "attendance": self.attendance_on, "threshold": self.threshold,
                "fps": round(self.fps, 1), "faces": len(self.results), "results": self.results,
                "error": self.error,
                "capture": {k: c[k] for k in ("name", "target", "count", "status", "done")},
                "recent_marks": self.recent_marks[:10],
                "present_today": sorted(self.attendance.marked) if self.attendance else [],
            }


# ---------------------------------------------------------------------- data helpers
def model_info():
    trained = os.path.exists(config.MODEL_PATH) and os.path.exists(config.LABELS_PATH)
    info = {"trained": trained, "people": [], "trained_at": None, "stale": False}
    if not trained:
        return info
    try:
        _, labels = load_model()
    except Exception:
        return {**info, "trained": False}
    mtime = os.path.getmtime(config.MODEL_PATH)
    info["people"] = sorted(labels.values())
    info["trained_at"] = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
    current = [p for p in list_people() if image_files(p)]
    newest = 0.0
    for p in current:
        folder = os.path.join(config.DATASET_DIR, p)
        newest = max([newest, os.path.getmtime(folder)] +
                     [os.path.getmtime(os.path.join(folder, f)) for f in image_files(p)[-3:]])
    info["stale"] = sorted(current) != info["people"] or newest > mtime + 1
    return info


def people_summary():
    out = []
    for p in list_people():
        files = image_files(p)
        out.append({"name": p, "images": len(files), "thumb": files[len(files) // 2] if files else None,
                    "samples": files[:: max(1, len(files) // 6)][:6]})
    return out


def delete_person(name):
    name = clean_name(name)
    folder = os.path.join(config.DATASET_DIR, name)
    if not name or not os.path.isdir(folder):
        raise FileNotFoundError(f"No person named '{name}'")
    shutil.rmtree(folder)


def attendance_dates():
    if not os.path.isdir(config.ATTENDANCE_DIR):
        return []
    return sorted((f[len("attendance_"):-4] for f in os.listdir(config.ATTENDANCE_DIR)
                   if f.startswith("attendance_") and f.endswith(".csv")), reverse=True)


def attendance_rows(date):
    path = attendance_path(date)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))
