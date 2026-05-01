@echo off
echo ========================================
echo   AI Exam Proctoring System
echo ========================================
echo.
echo Starting monitoring system...
echo Press 'q' in the video window to stop
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat
python src/main.py

pause
