# Scopy 1.5 Apple Silicon 移植版（非官方）

[English](README.md) | 简体中文

本项目基于 Analog Devices 的 [Scopy v1.5.0-rc1](https://github.com/analogdevicesinc/scopy/tree/v1.5.0-rc1)（提交 `438f13835ef65c8ff56a511532817575a04d7fa9`），尝试让 Scopy 在搭载 Apple Silicon 芯片的 Mac 上原生运行。这是非官方的社区修改版本。

主要修改包括 arm64 构建支持、内嵌 Python 路径隔离、重连稳定性改进和网络分析仪脚本坐标轴修正。`source/` 包含修改后的 Scopy 源码及 iio-emu；`native/` 包含构建脚本、依赖版本记录和补丁。

Scopy 使用 GPL-3.0-or-later 许可证，请保留原有版权及许可声明。iio-emu 还有额外的 ADI 许可条款，详见 [其许可证](source/iio-emu/LICENSE_ADIBSD)；其他依赖的来源和许可资料见 [第三方组件说明](third_party/NOTICES.md)。

## 测试情况

在一台 Apple Silicon Mac（macOS 27.0.1）和固件 v0.27 的 ADALM2000 上，已测试 USB 识别、三次重新连接、60 秒模拟输入、FFT 和 16 通道逻辑输入。尚未测试输出、校准、回环精度、实际拔插重连和长期稳定性。

独立构建的版本还通过了 10 项模拟设备回归测试，包括连接、采样、重连、会话保存和网络分析仪脚本。这些测试连接本机模拟器，不能替代真实设备的完整测试。

## 发布状态

项目仍处于**草稿阶段**。源码和锁定版本的依赖已在一台机器的独立环境中构建，但尚不能证明在其他机器上均可复现。应用安装包未包含在仓库中：构建产物含有本机路径，对应源码和第三方组件的再分发条件也需要进一步核对。

## 本地构建（实验性）

在 Apple Silicon Mac 上安装 Xcode 和命令行工具、Git、Python 3 和 [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html)，并确保终端可以找到 `micromamba`。在仓库根目录运行：

```sh
python3 native/bootstrap.py
MAMBA_ROOT_PREFIX="$PWD/native/mamba" micromamba create -y -p "$PWD/native/env" -f native/environment-explicit.txt
python3 native/build.py
mkdir -p outputs
python3 native/package.py
python3 native/verify.py
```

依赖获取脚本不会覆盖已存在的依赖源码目录。构建过程会下载第三方源码和 conda 包；包的 URL 已锁定，但校验值尚未与独立签名清单核对。生成的应用仅经过本地临时签名，未经过 Apple 公证。构建目标为 macOS 11 及以上，但目前只在上文所列的 macOS 版本上测试过。

运行仅使用模拟器的冒烟测试：

```sh
python3 native/tests/run_smoke.py version help script-basic connect-default analog-acquisition reconnect session-roundtrip digital-config network-sweep invalid-device
```

测试脚本会先检查本地服务是否标识为 ADALM2000 Demo，再连接本机模拟器；这些测试不会连接实体设备。

不要将本地构建环境、缓存、硬件标识、原始日志或设备采集数据提交到仓库。
