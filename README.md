# Real-Time Face Detection and Recognition System

**Computer Vision Lab Project**
Name: Raghav Sharma  |  Roll No.: PIET23CA047  |  B.Tech CSE (AI)
Poornima Institute of Engineering and Technology

---

## 1. Aim
To design and implement a real-time system that detects human faces in a live webcam feed and recognises known individuals, using the Viola-Jones (Haar cascade) detector and the LBPH (Local Binary Pattern Histogram) recogniser in OpenCV.

## 2. Objectives
- Detect one or more faces in real time from a webcam stream.
- Build a custom face dataset for each person.
- Train a face recognition model on that dataset.
- Identify known faces live, label unknown faces as "Unknown", and display a match score and FPS.
- (Extension) Automatically mark attendance of recognised people in a CSV file.

## 3. Tools & Technologies
| Item | Used |
|---|---|
| Language | Python 3.8+ |
| Library | OpenCV (`opencv-contrib-python`), NumPy, Flask (web dashboard) |
| Detector | Haar Cascade - `haarcascade_frontalface_default.xml` |
| Recogniser | LBPH Face Recognizer (`cv2.face`) |
| Hardware | Laptop/PC with webcam |

## 4. Theory

### 4.1 Face Detection - Viola-Jones Algorithm
1. **Haar-like features** - rectangular black/white patterns (edges, lines, centre-surround) that capture intensity differences, e.g. the eye region is darker than the cheeks.
2. **Integral image** - lets the sum of any rectangle be computed in O(1), so thousands of features can be evaluated quickly.
3. **AdaBoost** - selects a small set of the most discriminative features out of ~160,000 and combines weak classifiers into a strong one.
4. **Cascade of classifiers** - a sequence of stages; non-face windows are rejected in early stages, so only promising regions reach later, heavier stages. This makes detection real-time.
5. **Sliding window + image pyramid** - the detector scans the image at multiple scales (`scaleFactor`), and `minNeighbors` removes weak/overlapping detections.

### 4.2 Face Recognition - LBPH
1. For each pixel, compare it with its 8 neighbours (radius 1). Neighbour >= centre -> 1, else 0. This gives an 8-bit binary number (the LBP code, 0-255).
2. The LBP image is divided into an 8x8 grid of cells.
3. A 256-bin histogram is computed for each cell; all histograms are concatenated into one feature vector.
4. **Training** stores the histogram of every training image with its label.
5. **Prediction** computes the histogram of the new face and finds the closest training histogram (Chi-square distance). The smaller the distance, the better the match. If distance > threshold, the face is labelled **Unknown**.

**Why LBPH?** It is robust to monotonic lighting changes, works with few samples, can be updated with new people, and runs fast on a CPU (no GPU needed).

## 5. System Architecture

```
 Webcam frame
     |
     v
 Grayscale + histogram equalisation
     |
     v
 Haar Cascade face detection  --->  bounding boxes (x, y, w, h)
     |
     v
 Crop face -> resize 200x200 -> equalise
     |
     v
 LBPH recogniser  --->  (label ID, distance)
     |
     v
 distance <= threshold ?  -- yes --> Name + match %  (+ attendance CSV)
                          -- no  --> "Unknown"
     |
     v
 Draw boxes, labels, FPS on frame -> display
```

## 6. Project Structure
```
face_recognition_system/
|-- main.py              # menu launcher for all modules
|-- config.py            # all settings (paths, thresholds, camera)
|-- utils.py             # shared helpers (detector, preprocessing, FPS, drawing)
|-- detect_faces.py      # Module 1: real-time face (+eye) detection
|-- capture_faces.py     # Module 2: dataset collection
|-- train_model.py       # Module 3: LBPH training + accuracy evaluation
|-- recognize_faces.py   # Module 4: real-time recognition + attendance
|-- app.py               # Web dashboard server (Flask)
|-- engine.py            # Camera engine used by the dashboard (detect / recognize / capture)
|-- templates/index.html # Dashboard page
|-- static/              # style.css, app.js
|-- run.bat              # Windows: double-click to install deps + open dashboard
|-- requirements.txt
|-- dataset/             # created automatically: dataset/<name>/*.jpg
|-- trainer/             # lbph_model.yml, labels.json
|-- attendance/          # attendance_<date>.csv
`-- screenshots/         # saved with 's' key
```

## 7. Algorithm
1. Start.
2. Load Haar cascade classifier.
3. **Dataset collection:** open webcam; for each frame convert to grayscale and detect faces; if exactly one face is found, crop, resize to 200x200, equalise and save; repeat until N samples are collected.
4. **Training:** read all images, assign an integer ID to each person folder, train LBPH, save model and label map.
5. **Recognition:** open webcam; for every frame detect faces; for each face preprocess and call `predict()`; if distance <= threshold show the name, else show "Unknown"; optionally log attendance.
6. Display output with bounding boxes, labels and FPS.
7. Press `q` to stop. End.

## 8. Installation
```bash
pip install -r requirements.txt
```
> Use `opencv-contrib-python` (not plain `opencv-python`), because the `cv2.face` module is in contrib. If both are installed, uninstall both and install only contrib.

## 9. How to Run

**Option A - web dashboard (recommended)**
```bash
python app.py
```
The browser opens at http://127.0.0.1:5000 (on Windows you can also double-click `run.bat`).

| Page | What it does |
|---|---|
| Dashboard | Stats, quick-start checklist, 7-day attendance chart, today's attendance, screenshots |
| Live Camera | Detect (with optional eyes) or Recognise mode, live FPS/face list with match %, threshold slider, attendance toggle, camera selector, screenshots |
| Register Person | Name + sample count, live capture with progress ring, then one-click training |
| People | Dataset gallery with sample quality, add more samples, delete person |
| Train Model | Train with optional 80/20 accuracy evaluation, per-person stats and log |
| Attendance | Pick a date, present/absent lists, attendance rate, remove wrong entries, export CSV |
| Image Test | Drag and drop a photo to detect or recognise faces in it |

The camera switches off automatically when you leave the Live/Register page.

**Option B - console menu**
```bash
python main.py
```

**Option C - individual scripts**
```bash
# 1. Face detection only
python detect_faces.py
python detect_faces.py --eyes
python detect_faces.py --image photo.jpg

# 2. Register people (repeat for each person)
python capture_faces.py --name Raghav
python capture_faces.py --name Aman

# 3. Train (with accuracy report)
python train_model.py --eval

# 4. Real-time recognition
python recognize_faces.py
python recognize_faces.py --attendance
python recognize_faces.py --threshold 60      # stricter
python recognize_faces.py --image group.jpg
```
**Keys:** `q` quit, `s` save screenshot.

## 10. Output (expected)
- **Detection:** green boxes around each face, with FPS and face count in the top-left corner.
- **Capture:** progress bar, plus warnings such as "No face detected" or "Only ONE person please".
- **Training (console):**
  ```
  [0] Aman      60 images
  [1] Raghav    60 images
  [EVAL] Test samples: 24 | Correct: 23 | Rejected as Unknown: 1 | Accuracy: 95.83%
  [DONE] 2 person(s), 120 images
  ```
- **Recognition:** green box with `Name (match%)` for known people, red box with `Unknown` for others.
- **Attendance:** `attendance/attendance_2026-11-17.csv`
  ```
  Name,Date,Time,Match %
  Raghav,2026-11-17,13:20:41,58.3
  ```

*(Paste your own screenshots from the `screenshots/` folder here for the record.)*

## 11. Results & Observations
- Detection runs at roughly 20-30 FPS on a normal laptop CPU at 640x480.
- With about 60 samples per person in decent lighting, recognition accuracy is typically above 90%.
- Accuracy drops with side profiles, very dim light, or heavy occlusion (mask, hand).
- Lowering the threshold reduces false matches but increases "Unknown" results. Tune it between 55 and 80.

## 12. Limitations & Future Scope
- Haar cascades work best on frontal faces. A DNN detector (SSD/ResNet, MTCNN, RetinaFace) would handle pose better.
- LBPH is a classical method. Deep embeddings (FaceNet, ArcFace, `face_recognition`/dlib) give higher accuracy at scale.
- Add liveness detection (blink/motion) to prevent photo spoofing.
- Add a database plus web dashboard for attendance, and deploy on Raspberry Pi/Jetson.

## 13. Conclusion
A real-time face detection and recognition system was implemented with OpenCV. The Viola-Jones Haar cascade gives fast, reliable frontal-face detection, and LBPH provides lightweight, lighting-robust recognition that runs on a CPU in real time. The system also supports dataset creation, accuracy evaluation, unknown-face rejection and automatic attendance logging.

## 14. Viva Questions
1. **Difference between face detection and face recognition?** Detection finds *where* faces are. Recognition identifies *whose* face it is.
2. **What is an integral image?** A table where each pixel stores the sum of all pixels above and to the left of it, so any rectangle sum takes 4 lookups.
3. **Role of AdaBoost in Viola-Jones?** It selects the best features and combines weak classifiers into a strong classifier.
4. **Why a cascade?** It rejects most non-face regions early, which saves computation and allows real-time detection.
5. **What do `scaleFactor` and `minNeighbors` do?** `scaleFactor` is the pyramid resize step. `minNeighbors` is how many overlapping detections are needed to accept a face.
6. **Why convert to grayscale?** Haar/LBP features use intensity only, and grayscale reduces computation 3x.
7. **Why histogram equalisation?** It spreads out intensity values and reduces the effect of lighting variation.
8. **What does LBPH's "confidence" mean?** It is a distance: lower means a better match. 0 is a perfect match.
9. **Other recognisers in OpenCV?** Eigenfaces (PCA) and Fisherfaces (LDA). LBPH is more robust to lighting and supports incremental updates.
10. **How would you improve accuracy?** More varied samples, better lighting, a DNN detector, and deep face embeddings.
