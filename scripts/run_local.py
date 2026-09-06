"""Run both local services and terminate their process trees on Ctrl+C."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def available(port: int) -> None:
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1", port))
        except OSError as exc:
            raise SystemExit(f"Port {port} is occupied. Stop the existing service first.") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", action="store_true", help="Install dependencies before starting")
    parser.add_argument("--no-demo", action="store_true", help="Disable seed data; use a fresh database")
    args = parser.parse_args()
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not npm:
        raise SystemExit("Node.js and npm are required. Install Node.js 22 or newer.")
    if args.install:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(ROOT / "backend/requirements.txt")], check=True)
        subprocess.run([npm, "ci"], cwd=ROOT / "frontend", check=True)
    if not (ROOT / "frontend/node_modules").exists():
        raise SystemExit("Dependencies are missing. Run this command again with --install.")
    available(8000)
    available(3000)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(ROOT), str(ROOT / "backend"), env.get("PYTHONPATH", "")])
    if args.no_demo:
        env["NETRA_SEED_DEMO"] = "false"
    children: list[subprocess.Popen] = []
    flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    try:
        children.append(subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"], cwd=ROOT, env=env, creationflags=flags, start_new_session=os.name != "nt"))
        deadline = time.monotonic() + 45
        while True:
            if children[0].poll() is not None:
                raise RuntimeError("Backend exited before readiness. See the error above.")
            try:
                with urlopen("http://127.0.0.1:8000/health", timeout=2) as response:
                    if response.status == 200:
                        break
            except OSError:
                pass
            if time.monotonic() > deadline:
                raise RuntimeError("Backend did not become ready within 45 seconds.")
            time.sleep(0.5)
        children.append(subprocess.Popen([npm, "run", "dev", "--", "--host", "127.0.0.1", "--port", "3000", "--strictPort"], cwd=ROOT / "frontend", env=env, creationflags=flags, start_new_session=os.name != "nt"))
        print("\nNETRA-X: http://localhost:3000\nAPI reference: http://localhost:8000/docs\nPress Ctrl+C to stop both services.\n", flush=True)
        while all(child.poll() is None for child in children):
            time.sleep(0.5)
        raise RuntimeError("A service stopped unexpectedly. See its output above.")
    except KeyboardInterrupt:
        print("\nStopping NETRA-X...")
    finally:
        for child in reversed(children):
            if child.poll() is None:
                if os.name == "nt":
                    subprocess.run(["taskkill", "/PID", str(child.pid), "/T", "/F"], capture_output=True)
                else:
                    os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    child.kill()


if __name__ == "__main__":
    main()
