"""
Real-Time Face Detection and Recognition System - menu launcher.
Run:  python main.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

MENU = """
==============================================
  REAL-TIME FACE DETECTION & RECOGNITION
==============================================
  1. Face detection only (webcam)
  2. Face + eye detection (webcam)
  3. Register new person (capture dataset)
  4. Train model
  5. Train model + show accuracy
  6. Real-time recognition
  7. Real-time recognition + attendance
  8. Open web dashboard (recommended)
  0. Exit
----------------------------------------------"""


def run(script, *args):
    subprocess.run([sys.executable, os.path.join(HERE, script), *args])


def main():
    while True:
        print(MENU)
        choice = input("Select option: ").strip()
        if choice == "1":
            run("detect_faces.py")
        elif choice == "2":
            run("detect_faces.py", "--eyes")
        elif choice == "3":
            name = input("Enter person's name: ").strip()
            if name:
                run("capture_faces.py", "--name", name)
        elif choice == "4":
            run("train_model.py")
        elif choice == "5":
            run("train_model.py", "--eval")
        elif choice == "6":
            run("recognize_faces.py")
        elif choice == "7":
            run("recognize_faces.py", "--attendance")
        elif choice == "8":
            run("app.py")
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
