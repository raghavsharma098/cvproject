"""
Central configuration for the Real-Time Face Detection & Recognition System.
Change values here instead of editing individual scripts.
"""
import os
import cv2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- Paths ----------
DATASET_DIR = os.path.join(BASE_DIR, "dataset")          # dataset/<person_name>/*.jpg
MODEL_DIR = os.path.join(BASE_DIR, "trainer")
MODEL_PATH = os.path.join(MODEL_DIR, "lbph_model.yml")
LABELS_PATH = os.path.join(MODEL_DIR, "labels.json")
ATTENDANCE_DIR = os.path.join(BASE_DIR, "attendance")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "screenshots")

# Haar cascades ship with OpenCV - no download needed
FACE_CASCADE_PATH = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
EYE_CASCADE_PATH = os.path.join(cv2.data.haarcascades, "haarcascade_eye.xml")

# ---------- Camera ----------
CAMERA_INDEX = 0            # 0 = default webcam
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# ---------- Detection (Viola-Jones / Haar) ----------
SCALE_FACTOR = 1.2          # image pyramid step
MIN_NEIGHBORS = 5           # higher = fewer false positives
MIN_FACE_SIZE = (60, 60)

# ---------- Dataset / Recognition (LBPH) ----------
FACE_SIZE = (200, 200)      # every face is resized to this before train/predict
SAMPLES_PER_PERSON = 60
LBPH_RADIUS = 1
LBPH_NEIGHBORS = 8
LBPH_GRID_X = 8
LBPH_GRID_Y = 8
# LBPH returns a *distance* (lower = better match).
# Predictions with distance above this are reported as "Unknown".
CONFIDENCE_THRESHOLD = 70.0
SAMPLE_DELAY = 0.12         # seconds between saved samples during capture

# ---------- Web dashboard ----------
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
WEB_HOST = "127.0.0.1"
WEB_PORT = 5000
CAMERA_IDLE_TIMEOUT = 20    # seconds: camera switches off when nobody watches the feed
