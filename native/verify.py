#!/usr/bin/env python3
"""Audit the packaged executable files, signatures and dependency closure."""
import json
from pathlib import Path
import re
import subprocess
import sys

from package import APP, macho, output

if len(sys.argv) > 1:
    APP = Path(sys.argv[1]).resolve()

items = []
for path in sorted(APP.rglob("*")):
    if not macho(path):
        continue
    architectures = output("lipo", "-archs", path).strip().split()
    if architectures != ["arm64"]:
        raise RuntimeError(f"Unexpected architecture: {path}: {architectures}")
    subprocess.run(["codesign", "--verify", "--strict", str(path)], check=True, capture_output=True)
    identity = output("otool", "-D", path).splitlines()[1:]
    dependencies = re.findall(r"^\s+(.+?) \(compatibility version", output("otool", "-L", path), re.M)
    for dependency in dependencies:
        if dependency in identity or dependency.startswith(("/System/Library/", "/usr/lib/")):
            continue
        if not dependency.startswith("@loader_path/"):
            raise RuntimeError(f"External dependency: {path}: {dependency}")
        resolved = (path.parent / dependency[len("@loader_path/"):]).resolve()
        if not resolved.is_relative_to(APP.resolve()) or not resolved.is_file():
            raise RuntimeError(f"Missing or external dependency: {path}: {dependency}")
    items.append(str(path.relative_to(APP)))
subprocess.run(["codesign", "--verify", "--deep", "--strict", str(APP)], check=True)
report = {"result": "passed", "architecture": "arm64", "macho_count": len(items),
          "all_macho_signatures_valid": True, "all_non_system_dependencies_bundled": True,
          "files": items}
target = APP.parent / "arm64-verification.json"
target.write_text(json.dumps(report, indent=2) + "\n")
print(f"PASS: {len(items)} arm64 binaries, individual signatures valid, all non-system dependencies bundled.")
