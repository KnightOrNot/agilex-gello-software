# agilex-gello-software

基于 [wuphilipp/gello_software](https://github.com/wuphilipp/gello_software) 的 GELLO 库与通用实验工具。使用 Python 3.11、uv 和 src 包布局，保留主手读取、设备校准、机器人抽象及上游 YAM/ROS2/仿真工作流。

PiPER-X 项目的设备组合、ZMQ 客户端、JS 定位、跟随与 raw 录制已迁入 `agilex-controller`。库本身不依赖 controller、AgileX SDK 或 LeRobot。

## 安装

```bash
uv sync --frozen
uv run agilex-gello-software --help
```

基础依赖只满足主手和基础工具。需要上游可选功能时安装相应 extra：

```bash
uv sync --frozen --extra simulation
uv sync --frozen --extra robots
uv sync --frozen --extra camera
```

`full` 包含全部可选依赖。仿真模型需单独初始化；普通主手读取不需要下载。系统依赖、串口权限和仿真准备见[安装指南](docs/installation.md)。

## 职责与目录

```text
src/agilex_gello_software/  主手 API、驱动、机器人抽象与 CLI
configs/                  YAML 示例、模板与生成配置
experiments/              上游实验入口的兼容包装
scripts/                  校准、配置生成与辅助工具
tests/                    CLI 和硬件生命周期回归
ros2/                     独立 ROS2 工作流
third_party/              MuJoCo Menagerie submodule
imgs/                     硬件与校准参考图片
docs/                     架构、安装、参考与上游说明
```

## Python 接口

应用可以沿用上游 `GelloAgent`，显式传入自己的 `DynamixelRobotConfig`：

```python
from agilex_gello_software.agents.gello_agent import GelloAgent

# device_config 是当前设备经过验证的 DynamixelRobotConfig。
agent = GelloAgent(port=port, dynamixel_config=device_config, start_joints=start_joints)
try:
    joints = agent.act({})
finally:
    agent.close()
```

设备配置只描述电机 ID、offset、方向和夹爪端点。应用自行决定如何映射到从臂、如何发送命令及如何记录数据。真实驱动初始化失败会显式报错；初始化异常和正常退出均释放串口。

`PORT_CONFIG_MAP` 保留上游示例设备。当前 PiPER-X 安装的 FTBM4Z46 标定移到了 controller 的 `config/default.toml`，通过显式配置传入，不再占用库的 YAM 示例配置。

## 独立命令

| 命令 | 用途 |
| --- | --- |
| `read` | 使用库端口表只读 GELLO |
| `launch-yaml` | 上游 YAML 工作流 |
| `launch-nodes` | 上游机器人服务 |
| `camera-server` / `camera-client` | 上游相机实验工具 |
| `quick-run` / `run-env` | 上游通用环境与演示 |

具体参数执行 `uv run agilex-gello-software COMMAND --help`。部分命令会控制真实设备或需要 extra；按上游文档准备硬件。

## PiPER-X 命令迁移

在 controller 根目录使用：

| 原入口 | 新入口 |
| --- | --- |
| `agilex-gello-software follow` | `uv run agilex-controller follow` |
| `agilex-gello-software follow-record` | `uv run agilex-controller record` |
| `agilex-gello-software movejs` | `uv run agilex-controller movejs` |
| 当前安装的主手读取 | `uv run agilex-controller read` |

PiPER-X 专用实验包装和 raw recorder 已移出；默认频率、映射、采集与安全退出以 controller 文档为准。

## 开发与文档

```bash
uv run --frozen pytest
uv run --frozen ruff check src tests experiments scripts --select E9,F63,F7,F82
uv build
```

测试使用模拟驱动，不打开真实串口。库默认 pytest 仅收集 `tests/`；源码目录中的硬件诊断脚本不属于该测试集。

- [架构与数据流](docs/index.md)
- [安装指南](docs/installation.md)
- [CLI 参考](docs/reference/cli.md)
- [设备配置](docs/reference/config.md)
- [故障排查](docs/reference/errors.md)
- [贡献指南](CONTRIBUTING.md)
- [版本记录](CHANGELOG.md)
- [上游差异说明](docs/UPSTREAM.md)
- [保留的上游说明](docs/OFFICIAL.md)
- [ROS2 文档](ros2/README.md)
- [MIT License](LICENSE)

保留 Philipp Wu 的 MIT 版权声明。FACTR 与模型等第三方组件继续适用各自许可，来源见[架构文档](docs/index.md#来源与许可)。
