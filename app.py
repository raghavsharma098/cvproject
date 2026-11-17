"""
FaceVision - web dashboard for the Real-Time Face Detection & Recognition System.

Run:   python app.py          then open http://127.0.0.1:5000
"""
import base64
import os
import threading
import webbrowser
from datetime import datetime, timedelta

import cv2
import numpy as np
from flask import Flask, Response, jsonify, render_template, request, send_from_directory, abort

import config
import engine
from utils import clean_name, detect_faces, draw_box
from train_model import list_people, image_files
from recognize_faces import load_model, recognise_frame

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
camera = engine.CameraService()
train_lock = threading.Lock()


def ok(**data):
    return jsonify({"ok": True, **data})


def fail(msg, code=400):
    return jsonify({"ok": False, "error": str(msg)}), code


@app.errorhandler(Exception)
def handle_error(e):
    code = getattr(e, "code", 500)
    if isinstance(code, int) and code < 500 and not request.path.startswith("/api/"):
        return e
    return fail(e, code if isinstance(code, int) else 500)


# ---------------------------------------------------------------- pages / media
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    if not camera.running:
        abort(404)
    return Response(camera.mjpeg(), mimetype="multipart/x-mixed-replace; boundary=frame",
                    headers={"Cache-Control": "no-store"})


@app.route("/dataset/<person>/<filename>")
def dataset_image(person, filename):
    person = clean_name(person)
    if person not in list_people():
        abort(404)
    return send_from_directory(os.path.join(config.DATASET_DIR, person), filename)


@app.route("/screenshots/<filename>")
def screenshot_file(filename):
    return send_from_directory(config.SCREENSHOT_DIR, filename)


# ---------------------------------------------------------------- camera
@app.post("/api/camera/start")
def camera_start():
    d = request.get_json(silent=True) or {}
    try:
        camera.start(d.get("mode", "detect"), camera=d.get("camera"), eyes=d.get("eyes"),
                     attendance=d.get("attendance"), threshold=d.get("threshold"),
                     name=d.get("name"), samples=d.get("samples"))
    except (ValueError, RuntimeError) as e:
        return fail(e)
    return ok(status=camera.status())


@app.post("/api/camera/stop")
def camera_stop():
    camera.stop()
    return ok(status=camera.status())


@app.post("/api/camera/settings")
def camera_settings():
    d = request.get_json(silent=True) or {}
    try:
        camera.update_settings(eyes=d.get("eyes"), attendance=d.get("attendance"),
                               threshold=d.get("threshold"))
    except (ValueError, RuntimeError) as e:
        return fail(e)
    return ok(status=camera.status())


@app.get("/api/status")
def status():
    return ok(status=camera.status())


@app.post("/api/screenshot")
def screenshot():
    try:
        name = camera.screenshot()
    except RuntimeError as e:
        return fail(e)
    return ok(file=name, url=f"/screenshots/{name}")


@app.get("/api/screenshots")
def screenshots():
    files = sorted((f for f in os.listdir(config.SCREENSHOT_DIR) if f.lower().endswith(".jpg")),
                   key=lambda f: os.path.getmtime(os.path.join(config.SCREENSHOT_DIR, f)), reverse=True)
    return ok(files=[{"name": f, "url": f"/screenshots/{f}"} for f in files[:24]])


# ---------------------------------------------------------------- people / model
@app.get("/api/people")
def people():
    return ok(people=engine.people_summary(), model=engine.model_info())


@app.delete("/api/people/<name>")
def delete_person(name):
    if camera.mode == "capture" and camera.capture.get("name") == clean_name(name):
        camera.stop()
    try:
        engine.delete_person(name)
    except FileNotFoundError as e:
        return fail(e, 404)
    return ok(people=engine.people_summary(), model=engine.model_info())


@app.post("/api/train")
def train():
    d = request.get_json(silent=True) or {}
    if not train_lock.acquire(blocking=False):
        return fail("Training is already running.")
    try:
        result = camera.train(bool(d.get("eval", True)))
    except RuntimeError as e:
        return fail(e)
    finally:
        train_lock.release()
    return ok(result=result, model=engine.model_info())


@app.get("/api/overview")
def overview():
    ppl = engine.people_summary()
    today = datetime.now().strftime("%Y-%m-%d")
    week = []
    for i in range(6, -1, -1):
        day = datetime.now() - timedelta(days=i)
        week.append({"date": day.strftime("%Y-%m-%d"), "label": day.strftime("%a"),
                     "count": len(engine.attendance_rows(day.strftime("%Y-%m-%d")))})
    shots = len([f for f in os.listdir(config.SCREENSHOT_DIR) if f.lower().endswith(".jpg")])
    return ok(people=len(ppl), images=sum(p["images"] for p in ppl), model=engine.model_info(),
              today=engine.attendance_rows(today), week=week, screenshots=shots,
              total_people=[p["name"] for p in ppl])


# ---------------------------------------------------------------- attendance
@app.get("/api/attendance")
def attendance():
    dates = engine.attendance_dates()
    date = request.args.get("date") or (dates[0] if dates else datetime.now().strftime("%Y-%m-%d"))
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return fail("Bad date")
    rows = engine.attendance_rows(date)
    registered = list_people()
    present = {r["Name"] for r in rows}
    return ok(date=date, dates=dates, rows=rows,
              absent=[p for p in registered if p not in present], registered=len(registered))


@app.get("/api/attendance/download")
def attendance_download():
    date = request.args.get("date", "")
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        abort(400)
    return send_from_directory(config.ATTENDANCE_DIR, f"attendance_{date}.csv", as_attachment=True)


@app.delete("/api/attendance/<date>/<name>")
def attendance_remove(date, name):
    """Remove one person's entry (e.g. a false match)."""
    import csv
    rows = engine.attendance_rows(date)
    keep = [r for r in rows if r["Name"] != name]
    if len(keep) == len(rows):
        return fail("Entry not found", 404)
    from recognize_faces import attendance_path
    with open(attendance_path(date), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Name", "Date", "Time", "Match %"])
        w.writeheader()
        w.writerows(keep)
    if camera.attendance and camera.attendance.date == date:
        camera.attendance.marked.discard(name)
    return ok()


# ---------------------------------------------------------------- still image
@app.post("/api/image")
def analyse_image():
    f = request.files.get("image")
    if not f:
        return fail("No image uploaded")
    img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return fail("Could not read that file as an image")
    h, w = img.shape[:2]
    if max(h, w) > 1280:
        s = 1280 / max(h, w)
        img = cv2.resize(img, (int(w * s), int(h * s)))
    mode = request.form.get("mode", "recognize")
    threshold = float(request.form.get("threshold", config.CONFIDENCE_THRESHOLD))
    if mode == "recognize":
        try:
            rec, labels = load_model()
        except RuntimeError as e:
            return fail(e)
        _, results = recognise_frame(img, camera.face_det, rec, labels, threshold)
    else:
        gray = cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
        results = []
        for i, b in enumerate(detect_faces(camera.face_det, gray), 1):
            draw_box(img, b, f"Face {i}", (240, 180, 60))
            results.append({"name": f"Face {i}", "known": None, "box": [int(v) for v in b]})
    _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 88])
    return ok(image="data:image/jpeg;base64," + base64.b64encode(buf).decode(), results=results)


if __name__ == "__main__":
    url = f"http://{config.WEB_HOST}:{config.WEB_PORT}"
    print(f"\n  FaceVision dashboard running at {url}\n  Press Ctrl+C to stop.\n")
    if os.environ.get("NO_BROWSER") != "1":
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    app.run(host=config.WEB_HOST, port=config.WEB_PORT, threaded=True, debug=False)
