@echo off
cd /d "%~dp0"
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Python may be available as py on Windows.
  py -m pip install -r requirements.txt
)
python server.py
if errorlevel 1 py server.py
pause
