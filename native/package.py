#!/usr/bin/env python3
"""Create a self-contained arm64 Scopy.app from the local native build."""
from collections import deque
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent
NATIVE = ROOT / "native"
ENV = NATIVE / "env"
PREFIX = NATIVE / "prefix"
APP = ROOT / "outputs/Scopy-arm64.app"
FRAMEWORKS = APP / "Contents/Frameworks"
MAGICS = (b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe", b"\xca\xfe\xba\xbe")


def macho(path):
    if not path.is_file() or path.is_symlink():
        return False
    with path.open("rb") as stream:
        return stream.read(4) in MAGICS


def output(*args):
    return subprocess.check_output(list(map(str, args)), text=True)


def resolve(dependency, origin):
    # libm2k's conda build names its original libiio path. Replace that ABI-
    # compatible library consistently with our uncompressed 0.26 build.
    if Path(dependency).name.startswith("libiio."):
        replacement = PREFIX / "lib" / Path(dependency).name
        if replacement.is_file():
            return replacement.resolve()
    if dependency.startswith("@loader_path/"):
        candidates = [origin.parent / dependency[len("@loader_path/"):]]
    elif dependency.startswith("@executable_path/"):
        candidates = [NATIVE / "build/scopy/Scopy.app/Contents/MacOS" / dependency[len("@executable_path/"):]]
    elif dependency.startswith("@rpath/"):
        relative = dependency[len("@rpath/"):]
        candidates = [origin.parent / relative, PREFIX / "lib" / relative, ENV / "lib" / relative]
    else:
        candidates = [Path(dependency), PREFIX / "lib" / dependency, ENV / "lib" / dependency]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(f"Cannot resolve {dependency} required by {origin}")


def package():
    source_app = NATIVE / "build/scopy/Scopy.app"
    if not source_app.is_dir():
        raise FileNotFoundError("Build the intermediate app first: python3 native/build.py scopy")
    if APP.exists():
        shutil.rmtree(APP)
    subprocess.run(["ditto", str(source_app), str(APP)], check=True)
    FRAMEWORKS.mkdir(parents=True, exist_ok=True)
    resources = APP / "Contents/Resources"
    shutil.copy2(NATIVE / "build/scopy/iio-emu/iio-emu", APP / "Contents/MacOS/iio-emu")
    python = resources / "python/lib/python3.12"
    shutil.copytree(ENV / "lib/python3.12", python,
                    ignore=shutil.ignore_patterns("site-packages", "__pycache__", "*.pyc", "test", "tests", "idlelib", "tkinter"))
    (python / "site-packages").mkdir()
    (resources / "qt.conf").write_text("[Paths]\nPlugins=plugins\n")
    info_path = APP / "Contents/Info.plist"
    with info_path.open("rb") as stream:
        info = plistlib.load(stream)
    info.update({"CFBundleIdentifier": "org.adi.Scopy.arm64", "CFBundleName": "Scopy arm64",
                 "CFBundleDisplayName": "Scopy arm64", "CFBundleShortVersionString": "1.5.0",
                 "CFBundleVersion": "1.5.0", "LSMinimumSystemVersion": "11.0",
                 "LSArchitecturePriority": ["arm64"],
                 "LSEnvironment": {"PYTHONDONTWRITEBYTECODE": "1"}})
    with info_path.open("wb") as stream:
        plistlib.dump(info, stream)
    queue = deque((path, path) for path in APP.rglob("*") if macho(path))
    done = set()
    origins = {}
    while queue:
        path, origin = queue.popleft()
        if path in done:
            continue
        done.add(path)
        arches = output("lipo", "-archs", path).strip().split()
        if "arm64" not in arches:
            raise RuntimeError(f"Non-native code in bundle: {path}: {arches}")
        dependencies = re.findall(r"^\s+(.+?) \(compatibility version", output("otool", "-L", path), re.M)
        identity = output("otool", "-D", path).splitlines()[1:]
        for dependency in dependencies:
            if dependency in identity or dependency.startswith(("/System/Library/", "/usr/lib/")):
                continue
            source = resolve(dependency, origin)
            destination = FRAMEWORKS / source.name
            if destination not in origins:
                shutil.copy2(source, destination)
                origins[destination] = source
                queue.append((destination, source))
            elif origins[destination] != source:
                raise RuntimeError(f"Conflicting library names: {source}, {origins[destination]}")
            relative = os.path.relpath(destination, path.parent)
            subprocess.run(["install_name_tool", "-change", dependency, "@loader_path/" + relative, str(path)], check=True)
        listing = output("otool", "-l", path)
        for rpath in re.findall(r"cmd LC_RPATH\s+cmdsize \d+\s+path (.*?) \(offset", listing):
            subprocess.run(["install_name_tool", "-delete_rpath", rpath, str(path)], check=True)
        if identity:
            subprocess.run(["install_name_tool", "-id", "@rpath/" + path.name, str(path)], check=True)
    licenses = resources / "licenses"
    licenses.mkdir()
    for source in [ROOT / "source", ROOT / "source/iio-emu", *list((NATIVE / "src").iterdir())]:
        if not source.is_dir():
            continue
        for pattern in ("LICENSE*", "COPYING*", "COPYRIGHT*"):
            for item in source.glob(pattern):
                if item.is_file():
                    shutil.copy2(item, licenses / (source.name + "-" + item.name))
    for directory in (NATIVE / "mamba/pkgs").rglob("info/licenses"):
        shutil.copytree(directory, licenses / directory.parent.parent.name, dirs_exist_ok=True)
    report = {"application": APP.name, "macho_count": len(done), "architecture": "arm64",
              "bundled_libraries": {str(k.relative_to(APP)): str(v) for k, v in origins.items()}}
    (ROOT / "outputs/arm64-dependency-report.json").write_text(json.dumps(report, indent=2) + "\n")
    for path in sorted(done):
        if path == APP / "Contents/MacOS/Scopy":
            continue  # Signing the main executable implicitly signs its bundle.
        subprocess.run(["codesign", "--force", "--sign", "-", str(path)], check=True, capture_output=True)
    subprocess.run(["codesign", "--force", "--deep", "--sign", "-", str(APP)], check=True)
    subprocess.run(["codesign", "--verify", "--deep", "--strict", str(APP)], check=True)
    for path in sorted(done):
        subprocess.run(["codesign", "--verify", "--strict", str(path)], check=True, capture_output=True)
    # Keep Spotlight from offering the unbundled development executable.
    registry = "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
    # An unregistered development bundle can make lsregister return an error.
    # It is still safe to remove this generated build artifact.
    subprocess.run([registry, "-u", str(source_app)], check=False, capture_output=True)
    shutil.rmtree(source_app)  # Generated build product; the verified package is retained.
    print(f"Packaged {APP}: {len(done)} arm64 Mach-O files, {len(origins)} dependency libraries.")


if __name__ == "__main__":
    package()
