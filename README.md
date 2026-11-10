# Scopy 1.5 for Apple Silicon

English | [简体中文](README.zh-CN.md)

An Apple Silicon native port of Scopy 1.5 for macOS users working with the ADALM2000, based on Analog Devices' [Scopy v1.5.0-rc1](https://github.com/analogdevicesinc/scopy/tree/v1.5.0-rc1). This is an unofficial community port and is not an official Analog Devices release.

## Features

- Native Apple Silicon (arm64) support.
- Measurement and analysis with the ADALM2000.
- Improved embedded Python path isolation and device reconnection stability.
- Corrected network analyzer script axes.

## Compatibility

An actual experiment was completed successfully on an **Apple M6 device running macOS 27.0.1**. The build targets macOS 11 and later; compatibility with other devices and macOS versions has not been confirmed.

## Build from source

An Apple Silicon Mac, Xcode and its command-line tools, Git, Python 3, and [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html) are required. With `micromamba` on PATH, run the following from the repository root:

```sh
python3 native/bootstrap.py
MAMBA_ROOT_PREFIX="$PWD/native/mamba" micromamba create -y -p "$PWD/native/env" -f native/environment-explicit.txt
python3 native/build.py
mkdir -p outputs
python3 native/package.py
python3 native/verify.py
```

The build downloads third-party sources and packages; the bootstrap script refuses to overwrite existing source directories. The resulting app is locally ad-hoc signed and has not been notarized by Apple. No application archive is included in this repository: local paths in the build output and third-party redistribution requirements still need review.

## Project structure

- `source/`: modified Scopy source and iio-emu.
- `native/`: Apple Silicon build scripts, dependency pins and patches.
- `third_party/`: third-party dependency provenance and license materials.

## Credits and licenses

Thanks to the contributors to [Analog Devices Scopy](https://github.com/analogdevicesinc/scopy) and its dependencies. This port is based on upstream commit `438f13835ef65c8ff56a511532817575a04d7fa9`.

Scopy is licensed under [GPL-3.0-or-later](LICENSE). iio-emu is subject to additional [ADI license terms](source/iio-emu/LICENSE_ADIBSD); see [third_party/NOTICES.md](third_party/NOTICES.md) for third-party provenance and license information.
