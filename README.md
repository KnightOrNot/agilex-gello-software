# agilex-gello-software

在 [GELLO 上游](https://github.com/wuphilipp/gello_software) 基础上增加独立 `src/` 入口，供 agilex-controller 读取主手、显式传入校准并管理资源。上游 `gello/`、实验脚本、配置、ROS2 和 DynamixelSDK 保持固定基线；本项目继续使用 Python 3.11 和 uv。

上游硬件搭建、通用机器人、ROS2、仿真与 FACTR 的完整说明见 [docs/OFFICIAL.md](docs/OFFICIAL.md)。本文说明当前 fork 的安装、开发与 controller 接入。

## 职责与目录

| 路径 | 责任 |
| --- | --- |
| `gello/` | 原生上游包与 Dynamixel 驱动，保留 `gello.*` 导入 |
| `experiments/`、`scripts/`、`configs/`、`ros2/` | 上游原始工具与配置 |
| `third_party/DynamixelSDK/` | 上游固定的 SDK；Python 包由 uv 安装 |
| `src/agilex_gello_software/` | 本地 CLI、驱动/生命周期适配与上游校验清单 |
| `tests/`、`docs/` | 本地回归与当前项目文档 |

controller 负责客户端组合、主从映射、JS 定位、跟随与 raw 录制；converter 负责时间对齐与 LeRobot 输出。它们不是本库依赖。

## 安装与检查

在本仓库根目录执行；新 checkout 先初始化 SDK：

```bash
git submodule update --init third_party/DynamixelSDK
uv sync --frozen
uv run agilex-gello-software --help
```

作为 controller submodule 使用时，根项目的 `scripts/setup.sh` 会准备所需环境。开发中使用 controller 的 `--skip-submodules` 保留本地改动。

普通主手读取无需下载仿真模型；可选依赖与权限见[安装指南](docs/installation.md)。当前 PiPER-X 安装在 controller 根目录读取自己的 TOML 校准：

```bash
uv run agilex-controller read
```

## Python 接口

应用使用 `src/` 适配 API，导入路径保持兼容：

```python
from agilex_gello_software.agents.gello_agent import GelloAgent

# port、device_config 和 start_joints 由应用根据当前设备提供。
agent = GelloAgent(port=port, dynamixel_config=device_config, start_joints=start_joints)
try:
    joints = agent.act({})
finally:
    agent.close()
```

本地适配继承上游校准/滤波和 `act()`，保留真实失败、首帧等待、陈旧反馈与清理策略。直接导入 `gello.*` 使用的是原生上游行为，不会自动获得这些扩展，详见[架构](docs/index.md)。

## 命令与数采

本地 CLI 保留 `read` 和通用上游工具的入口；`gello` 是兼容命令别名。通用命令执行原始 `experiments/` 脚本，参数以 `COMMAND --help` 为准。

PiPER-X 的 `follow`、`record`、`movejs` 在 controller 中运行：

```bash
./scripts/start_gello_follow.sh
./scripts/start_data_record.sh
```

以上两个脚本从 controller 根目录执行；不要使用通用上游 `run-env` 代替当前应用流程。

## 开发验证

```bash
uv run --frozen pytest
uv run --frozen ruff check src tests
uv run --frozen ruff format --check src tests
uv run --frozen python -m agilex_gello_software.upstream
uv build
```

uv 统一管理安装、运行和构建。构建后端为 Hatchling，以同时打包原生 `gello` 和 `src/agilex_gello_software`，不移动或重写上游包。

- [架构与边界](docs/index.md)
- [安装](docs/installation.md)
- [CLI](docs/reference/cli.md)
- [配置](docs/reference/config.md)
- [排障](docs/reference/errors.md)
- [贡献指南](CONTRIBUTING.md)
- [上游基线与差异](docs/UPSTREAM.md)
- [上游开发说明](docs/OFFICIAL.md)
- [版本记录](CHANGELOG.md)

保留 [MIT 许可](LICENSE)及上游版权；DynamixelSDK、FACTR、模型和 ROS2 组件保留各自许可。
