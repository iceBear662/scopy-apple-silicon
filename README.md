# Scopy 1.5 for Apple Silicon (unofficial)

English | [简体中文](README.zh-CN.md)

Apple Silicon port based on [Analog Devices Scopy v1.5.0-rc1](https://github.com/analogdevicesinc/scopy/tree/v1.5.0-rc1), commit `438f13835ef65c8ff56a511532817575a04d7fa9`. This is an unofficial community modification. Scopy is licensed under GPL-3.0-or-later; retain the original copyright and license notices.

Changes include arm64 build support, embedded Python path isolation, reconnect stability and network analyzer script-axis corrections. `source/` includes the modified Scopy source and its iio-emu submodule. `native/` records build scripts, dependency pins and patches. The iio-emu component has additional ADI license terms; see `source/iio-emu/LICENSE_ADIBSD`.

The local build was tested on an Apple Silicon Mac with macOS 27.0.1 and an ADALM2000 on firmware v0.27: USB recognition, three reconnects, 60-second analog input, FFT and 16-channel logic input were tested. Outputs, calibration, loopback accuracy, physical unplug/replug and long-term stability were not tested.

## Release preparation status

This directory is a **draft**. The sources and pinned dependencies have been built in a separate local environment; this is one build on one machine, not proof of reproducibility on other machines. The application archive is not included while corresponding-source and third-party redistribution conditions remain under review. See [third-party provenance and audit limitations](third_party/NOTICES.md).

## Local build (experimental)

On an Apple Silicon Mac, install Xcode and its command-line tools, Git, Python 3 and [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html). From the repository root, with `micromamba` on PATH:

```sh
python3 native/bootstrap.py
MAMBA_ROOT_PREFIX="$PWD/native/mamba" micromamba create -y -p "$PWD/native/env" -f native/environment-explicit.txt
python3 native/build.py
mkdir -p outputs
python3 native/package.py
python3 native/verify.py
```

The bootstrap step refuses to overwrite existing dependency checkouts. This downloads third-party source and conda packages. The package URLs are pinned, but their hashes were not checked against an independently signed manifest. The output is locally ad-hoc signed and has not been notarized by Apple. The build targets macOS 11 or newer; only the local macOS version above has been tested. The current output contains local build paths and requires further privacy and license review before distribution.

For a local emulator-only smoke test, run `python3 native/tests/run_smoke.py version help script-basic connect-default analog-acquisition reconnect session-roundtrip digital-config network-sweep invalid-device`. The runner checks that the local server identifies itself as the ADALM2000 Demo before running; these cases connect to localhost, not a physical device. All ten cases passed on the independent local build.

Do not commit local build environments, caches, hardware identifiers, raw logs or device capture data.
