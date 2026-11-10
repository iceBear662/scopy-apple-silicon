#!/usr/bin/env python3
"""Fetch the exact dependency sources used by the Apple Silicon build."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent
lock = json.loads((ROOT / "native/source-lock.json").read_text())
for path, item in lock.items():
    if not path.startswith("native/src/"):
        continue
    target = ROOT / path
    if target.exists():
        raise SystemExit(f"Refusing to overwrite existing source: {target}")
    target.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(target)], check=True)
    subprocess.run(["git", "-C", str(target), "remote", "add", "origin", item["url"]], check=True)
    if target.name == "gnuradio":
        subprocess.run(["git", "-C", str(target), "sparse-checkout", "init", "--cone"], check=True)
        subprocess.run(["git", "-C", str(target), "sparse-checkout", "set", "gr-iio"], check=True)
    subprocess.run(["git", "-C", str(target), "fetch", "--depth=1", "origin", item["commit"]], check=True)
    subprocess.run(["git", "-C", str(target), "checkout", "--detach", "FETCH_HEAD"], check=True)
    if target.name == "libsigrokdecode":
        subprocess.run(["git", "-C", str(target), "apply", str(ROOT / "native/libsigrokdecode-arm64.patch")], check=True)
