@echo off
echo ========================================
echo   AI Exam Proctoring Dashboard
echo ========================================
echo.
echo Starting Flask dashboard on http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat
python src/dashboard/app.py

pause
