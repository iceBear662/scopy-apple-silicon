#!/usr/bin/env python3
"""Build Scopy 1.5's extra dependencies and application as native Apple arm64."""
import argparse
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent
NATIVE = ROOT / "native"
ENV = NATIVE / "env"
PREFIX = NATIVE / "prefix"
BUILD = NATIVE / "build"
LOGS = NATIVE / "logs"
env = os.environ.copy()
env.update({
    "PATH": f"{ENV}/bin:{env['PATH']}",
    "PKG_CONFIG_PATH": f"{PREFIX}/lib/pkgconfig:{ENV}/lib/pkgconfig:{ENV}/share/pkgconfig",
    "CMAKE_PREFIX_PATH": f"{PREFIX};{ENV}",
    "MACOSX_DEPLOYMENT_TARGET": "11.0",
    "TMPDIR": str(NATIVE / "tmp"),
    "CC": "/usr/bin/clang",
    "CXX": "/usr/bin/clang++",
    "PYTHON3": str(ENV / "bin/python3"),
    "PYTHONDONTWRITEBYTECODE": "1",
})


def run(args, cwd, logfile):
    print("Running:", " ".join(map(str, args)), flush=True)
    with (LOGS / logfile).open("a") as out:
        subprocess.run(list(map(str, args)), cwd=cwd, env=env, stdout=out, stderr=subprocess.STDOUT, check=True)


def cmake(name, source, *extra):
    directory = BUILD / name
    directory.mkdir(parents=True, exist_ok=True)
    logfile = name + ".log"
    run([ENV / "bin/cmake", "-S", source, "-B", directory, "-G", "Ninja",
         "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_OSX_ARCHITECTURES=arm64",
         "-DCMAKE_OSX_DEPLOYMENT_TARGET=11.0", f"-DCMAKE_INSTALL_PREFIX={PREFIX}",
         f"-DCMAKE_PREFIX_PATH={PREFIX};{ENV}", "-DCMAKE_FIND_FRAMEWORK=LAST",
         f"-DPython3_EXECUTABLE={ENV}/bin/python3", "-DENABLE_PYTHON=OFF",
         "-DENABLE_DOXYGEN=OFF", *extra], ROOT, logfile)
    run([ENV / "bin/cmake", "--build", directory, "--parallel", "6"], ROOT, logfile)
    if name != "scopy":
        run([ENV / "bin/cmake", "--install", directory], ROOT, logfile)


def modern_qt_sdk():
    # AGL was a 32-bit API and is absent from modern SDKs. Old Qt5 metadata
    # still lists it as a static UiTools dependency; Cocoa/OpenGL is sufficient.
    metadata = ENV / "lib/libQt5UiTools.prl"
    content = metadata.read_text()
    fixed = content.replace("-framework AGL", "").replace("-framework;AGL;", "")
    if content != fixed:
        temporary = metadata.with_suffix(".native-tmp")
        temporary.write_text(fixed)
        temporary.replace(metadata)  # Do not modify the conda package cache hardlink.


def qwt():
    source = NATIVE / "src/qwt"
    config = source / "qwtconfig.pri"
    text = config.read_text()
    marker = "# Scopy native build overrides"
    if marker not in text:
        text += f"\n{marker}\nQWT_INSTALL_PREFIX = {PREFIX}\nQWT_INSTALL_HEADERS = {PREFIX}/include/qwt\nQWT_INSTALL_LIBS = {PREFIX}/lib\nQWT_CONFIG -= QwtFramework QwtDesigner QwtExamples QwtPlayground QwtTests\n"
    if "# Native feature destination" not in text:
        text += f"\n# Native feature destination\nQWT_INSTALL_FEATURES = {PREFIX}/mkspecs/features\n"
    config.write_text(text)
    directory = BUILD / "qwt"
    directory.mkdir(parents=True, exist_ok=True)
    run([ENV / "bin/qmake", "-r", source / "qwt.pro", "QMAKE_APPLE_DEVICE_ARCHS=arm64",
         "QMAKE_MACOSX_DEPLOYMENT_TARGET=11.0", "-after",
         "QMAKE_LIBS_OPENGL=-framework OpenGL"], directory, "qwt.log")
    run(["make", "-j6"], directory, "qwt.log")
    run(["make", "install"], directory, "qwt.log")


def sigrok():
    source = NATIVE / "src/libsigrokdecode"
    directory = BUILD / "libsigrokdecode"
    directory.mkdir(parents=True, exist_ok=True)
    if not (source / "configure").exists():
        run(["./autogen.sh"], source, "libsigrokdecode.log")
    run([source / "configure", f"--prefix={PREFIX}", "--disable-static"], directory, "libsigrokdecode.log")
    run(["make", "-j6"], directory, "libsigrokdecode.log")
    run(["make", "install"], directory, "libsigrokdecode.log")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("targets", nargs="*", default=["libiio", "libtinyiiod", "gr-iio", "gr-scopy", "gr-m2k", "qwt", "libsigrokdecode", "scopy"])
    args = parser.parse_args()
    PREFIX.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    (NATIVE / "tmp").mkdir(parents=True, exist_ok=True)
    modern_qt_sdk()
    for target in args.targets:
        if target == "qwt":
            qwt()
        elif target == "libsigrokdecode":
            sigrok()
        elif target == "gr-iio":
            cmake(target, NATIVE / "gr-iio")
        elif target == "libiio":
            cmake(target, NATIVE / "src/libiio", "-DWITH_ZSTD=OFF", "-DOSX_PACKAGE=OFF",
                  "-DOSX_FRAMEWORK=OFF", "-DWITH_TESTS=OFF", "-DWITH_DOC=OFF",
                  "-DWITH_NETWORK_BACKEND=ON", "-DWITH_USB_BACKEND=ON",
                  "-DENABLE_DNS_SD=OFF", "-DPYTHON_BINDINGS=OFF",
                  "-DCMAKE_INSTALL_NAME_DIR=@rpath")
        elif target == "scopy":
            cmake(target, ROOT / "source", f"-DPYTHON_EXECUTABLE={ENV}/bin/python3",
                  f"-DQWT_INCLUDE_DIRS={PREFIX}/include/qwt",
                  f"-DCMAKE_CXX_FLAGS=-I{PREFIX}/include -I{ENV}/include",
                  f"-DCMAKE_EXE_LINKER_FLAGS=-L{PREFIX}/lib -L{ENV}/lib",
                  "-DBREAKPAD_HANDLER=OFF", "-DENABLE_MATIO=OFF")
        else:
            cmake(target, NATIVE / "src" / target, "-DDIGITAL=OFF", "-DBUILD_EXAMPLES=OFF")
