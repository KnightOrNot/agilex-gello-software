# 安装指南

## 基础环境

推荐 Linux、Python 3.11、Git 和 uv。以下命令在本仓库根目录执行；作为 controller submodule 使用时，也可以由 controller 的 `scripts/setup.sh` 准备环境。

```bash
uv sync --frozen
uv run agilex-gello-software --help
uv run agilex-gello-software read --help
```

使用 pyenv 管理解释器时，可显式传入已安装的 Python：

```bash
UV_NO_MANAGED_PYTHON=1 uv sync --frozen --python "$(pyenv which python)"
```

确认该解释器为 3.11。通常无需激活 `.venv`；通过 `uv run` 使用当前项目环境。

## 串口与校准

先检查 `/dev/serial/by-id/` 中的设备名和串口权限。Ubuntu 用户需要时执行 `sudo usermod -aG dialout "$USER"`，注销后重新登录。每个 GELLO 串口同一时间只允许一个程序持有；先停止跟随程序再读取或校准。

电机 ID、波特率、offset、方向和夹爪端点需要与设备一致。独立 `read` 要求端口已在库端口表中；当前 PiPER-X 安装应在 controller 根目录执行 `uv run agilex-controller read`，读取其 TOML 校准。配置方法见[设备配置](reference/config.md)。

## 可选工具

| extra | 用途 |
| --- | --- |
| `camera` | 上游 RealSense 实验，另需可用设备和系统驱动 |
| `simulation` | MuJoCo、dm-control、GUI 与相关计算依赖 |
| `robots` | UR、xArm、SpaceMouse 等可选接口 |
| `full` | 上述可选依赖合集 |

例如：

```bash
uv sync --frozen --extra simulation
git submodule update --init --recursive
```

普通主手读取无需 Menagerie。需要多个 extra 时，在一次 `uv sync` 中分别传入它们；后续仅同步基础环境可能移除可选包。I2RT、Polymetis、ROS2 等外部系统不是 `full` 自动提供的完整部署，按[上游存档](OFFICIAL.md)及 [ROS2 指南](../ros2/README.md)准备。

仿真需要图形/OpenGL 环境。资源位于其他 checkout 时按[路径配置](reference/config.md)设置环境变量。Docker 与完整 ROS2 工作流不属于默认 Python 测试的验证范围。
