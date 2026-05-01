"""
Single entry point to launch both the monitoring engine and dashboard together.
Run with: python run.py
"""
import subprocess
import sys
import os
import time
import threading
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, 'src')

# Resolve the Python executable inside the venv if it exists
_venv_python = os.path.join(ROOT, 'venv', 'Scripts', 'python.exe')  # Windows
if not os.path.exists(_venv_python):
    _venv_python = os.path.join(ROOT, 'venv', 'bin', 'python')      # Mac/Linux
PYTHON = _venv_python if os.path.exists(_venv_python) else sys.executable


def stream_output(process, prefix):
    """Print output from a subprocess with a label prefix."""
    for line in iter(process.stdout.readline, b''):
        print(f"[{prefix}] {line.decode(errors='replace').rstrip()}")


def main():
    print("Starting Exam Proctoring System...")
    print("=" * 45)

    # ── Launch Dashboard ──
    dashboard_proc = subprocess.Popen(
        [PYTHON, os.path.join(SRC, 'dashboard', 'app.py')],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=ROOT
    )
    threading.Thread(target=stream_output, args=(dashboard_proc, 'DASHBOARD'), daemon=True).start()
    print("[INFO] Dashboard starting...")

    # Give Flask a moment to bind the port before opening browser
    time.sleep(3)
    webbrowser.open('http://localhost:5000')
    print("[INFO] Dashboard opened at http://localhost:5000")

    # ── Launch Monitoring Engine ──
    monitor_env = os.environ.copy()
    monitor_env['PYTHONPATH'] = SRC

    monitor_proc = subprocess.Popen(
        [PYTHON, os.path.join(SRC, 'main.py')],
        cwd=ROOT,
        env=monitor_env
    )
    print("[INFO] Monitoring engine started. Press Q in the camera window to stop.")
    print("=" * 45)

    try:
        monitor_proc.wait()  # Block until monitoring window is closed (Q pressed)
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
    finally:
        monitor_proc.terminate()
        dashboard_proc.terminate()
        print("[INFO] All processes stopped.")


if __name__ == '__main__':
    main()
