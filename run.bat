@echo off
cd /d "%~dp0"
echo Installing requirements...
py -m pip install -q -r requirements.txt
echo Starting FaceVision dashboard...
py app.py
pause
