"""
Runs both the MedLife backend and frontend locally, together.

- Backend (FastAPI/uvicorn):        http://localhost:8000
- Frontend (static HTML, stdlib):   http://localhost:5500

No Node.js needed for the frontend — Python's built-in http.server
is enough for plain HTML/JS/CSS with no build step.

Usage:
    python3 run_dev.py

Stop both with Ctrl+C.
"""

import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
BACKEND_PORT = 8000
FRONTEND_PORT = 5500


def main():
    if not FRONTEND_DIR.exists():
        print(f"Error: expected a 'frontend' folder at {FRONTEND_DIR}, but it doesn't exist.")
        sys.exit(1)

    print(f"Starting backend  on http://localhost:{BACKEND_PORT}")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api_server:app", "--port", str(BACKEND_PORT)],
        cwd=PROJECT_ROOT,
    )

    print(f"Starting frontend on http://localhost:{FRONTEND_PORT}")
    frontend = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(FRONTEND_PORT)],
        cwd=FRONTEND_DIR,
    )

    print("\nBoth servers running. Press Ctrl+C to stop both.\n")

    try:
        # Wait on either process; if one dies unexpectedly, stop the other too.
        while True:
            time.sleep(1)
            if backend.poll() is not None:
                print("Backend exited unexpectedly.")
                break
            if frontend.poll() is not None:
                print("Frontend exited unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\nStopping both servers...")
    finally:
        for proc, name in ((backend, "backend"), (frontend, "frontend")):
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        print("Stopped.")


if __name__ == "__main__":
    main()
