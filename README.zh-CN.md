# Scopy 1.5 for Apple Silicon

简体中文 | [English](README.md)

Scopy 1.5 的 Apple Silicon 原生移植版，基于 Analog Devices 的 [Scopy v1.5.0-rc1](https://github.com/analogdevicesinc/scopy/tree/v1.5.0-rc1)，适用于使用 ADALM2000 的 macOS 用户。本项目是非官方社区移植，与 Analog Devices 官方发布版本无关。

## 特性

- 原生支持 Apple Silicon（arm64）。
- 支持使用 ADALM2000 进行测量与分析。
- 改进内嵌 Python 的路径隔离与设备重连稳定性。
- 修正网络分析仪脚本的坐标轴问题。

## 兼容性

已在搭载 **Apple M6 芯片、运行 macOS 27.0.1** 的设备上完成一次实际实验，测试通过。构建目标为 macOS 11 及以上；其他设备和系统版本的兼容性尚未确认。

## 从源码构建

需要 Apple Silicon Mac、Xcode 及命令行工具、Git、Python 3 和 [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html)。确保终端可以找到 `micromamba`，然后在仓库根目录运行：

```sh
python3 native/bootstrap.py
MAMBA_ROOT_PREFIX="$PWD/native/mamba" micromamba create -y -p "$PWD/native/env" -f native/environment-explicit.txt
python3 native/build.py
mkdir -p outputs
python3 native/package.py
python3 native/verify.py
```

构建过程会下载第三方源码和依赖包；依赖获取脚本不会覆盖已存在的源码目录。生成的应用使用本地临时签名，未经 Apple 公证。当前仓库不包含应用安装包；构建产物仍需处理本机路径，并完成第三方组件再分发条件的核对。

## 项目结构

- `source/`：修改后的 Scopy 源码及 iio-emu。
- `native/`：Apple Silicon 构建脚本、依赖版本和补丁。
- `third_party/`：第三方依赖来源及许可资料。

## 致谢与许可证

感谢 [Analog Devices Scopy](https://github.com/analogdevicesinc/scopy) 及其依赖项目的贡献者。此移植基于上游提交 `438f13835ef65c8ff56a511532817575a04d7fa9`。

Scopy 使用 [GPL-3.0-or-later](LICENSE) 许可证。iio-emu 适用额外的 [ADI 许可条款](source/iio-emu/LICENSE_ADIBSD)；第三方依赖的来源和许可信息见 [third_party/NOTICES.md](third_party/NOTICES.md)。
