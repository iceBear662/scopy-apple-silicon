#!/usr/bin/env python3
"""Run bounded CLI/backend checks against the packaged Scopy application."""
import argparse
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "native/test-results"
WORK = ROOT / "native/test-work"


def emulator_ready():
    try:
        with socket.create_connection(("127.0.0.1", 30431), timeout=0.1):
            return True
    except OSError:
        return False


def require_demo_server():
    # Never run output/calibration tests against an unrelated local IIO daemon.
    with socket.create_connection(("127.0.0.1", 30431), timeout=2) as connection:
        connection.sendall(b"PRINT\r\n")
        with connection.makefile("rb") as stream:
            size = int(stream.readline(32).strip())
            if not 0 < size < 131072:
                raise RuntimeError("Unexpected IIO context size")
            context = stream.read(size)
    if b"ADALM2000 Demo" not in context:
        raise RuntimeError("Tests require the ADALM2000 Demo emulator; refusing an unrelated service")


def start_emulator():
    if emulator_ready():
        require_demo_server()
        return None
    log = (RESULTS / "emulator.log").open("w")
    process = subprocess.Popen([str(ROOT / "outputs/Scopy-arm64.app/Contents/MacOS/iio-emu"), "adalm2000"],
                               cwd=WORK, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    for _ in range(40):
        if emulator_ready():
            require_demo_server()
            return process
        if process.poll() is not None:
            break
        time.sleep(0.05)
    raise RuntimeError("Demo emulator failed to start")


def run_case(name, args, timeout=35, app=None, gui=False):
    app = app or ROOT / "outputs/Scopy-arm64.app"
    directory = WORK / name
    directory.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update({"XDG_CONFIG_HOME": str(directory / "config"),
                "XDG_CACHE_HOME": str(directory / "cache"),
                "PYTHONDONTWRITEBYTECODE": "1"})
    if not gui:
        env["QT_QPA_PLATFORM"] = "offscreen"
    started = time.monotonic()
    log_path = RESULTS / (name + ".log")
    with log_path.open("w") as stream:
        process = subprocess.Popen([str(app / "Contents/MacOS/Scopy"), *map(str, args)],
                                   cwd=directory, env=env, stdout=stream, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        timed_out = False
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                code = process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                code = process.wait()
    result = {"name": name, "exit_code": code, "timeout": timed_out,
              "seconds": round(time.monotonic() - started, 2), "log": str(log_path)}
    print(json.dumps(result), flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", nargs="*", default=["version", "help", "script-basic", "connect-basic"])
    options = parser.parse_args()
    RESULTS.mkdir(exist_ok=True)
    WORK.mkdir(exist_ok=True)
    results = []
    emulator = start_emulator()
    try:
        for name in options.cases:
            if name in ("version", "help"):
                args = ["--" + name]
            else:
                args = ["--nogui", "--noopengl", "--script", ROOT / "native/tests" / (name + ".js")]
            results.append(run_case(name, args, timeout=90 if name in ("reconnect", "soak") else 35))
    finally:
        if emulator:
            emulator.terminate()
            emulator.wait(timeout=3)
    (RESULTS / "latest.json").write_text(json.dumps(results, indent=2) + "\n")
    raise SystemExit(0 if all(r["exit_code"] == 0 and not r["timeout"] for r in results) else 1)
