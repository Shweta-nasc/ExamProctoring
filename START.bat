@echo off
echo Starting Exam Proctoring System...
cd /d "%~dp0"
call venv\Scripts\activate.bat
python run.py
pause
