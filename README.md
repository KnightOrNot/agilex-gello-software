# agilex-gello-software

基于 [wuphilipp/gello_software](https://github.com/wuphilipp/gello_software) 的 GELLO 库与通用实验工具。使用 Python 3.11、uv 和 src 包布局，保留主手读取、设备校准、机器人抽象及上游 YAM/ROS2/仿真工作流。

PiPER-X 项目的设备组合、ZMQ 客户端、JS 定位、跟随与 raw 录制已迁入 `agilex-controller`。库本身不依赖 controller、AgileX SDK 或 LeRobot。

## 安装

```bash
uv sync --frozen
uv run agilex-gello-software --help
uv run pytest
```

基础依赖只满足主手和基础工具。需要上游可选功能时安装相应 extra：

```bash
uv sync --extra simulation
uv sync --extra robots
uv sync --extra camera
```

`full` 包含全部可选依赖。仿真模型仍需按上游说明单独初始化，普通主手读取不需要下载。

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
| 当前安装的主手读取 | `uv run agilex-controller read --json` |

PiPER-X 专用实验包装和 raw recorder 已移出；默认频率、映射、采集与安全退出以 controller 文档为准。

## 维护与来源

- [开发指南](docs/DEVELOPMENT.md)
- [上游差异说明](docs/UPSTREAM.md)
- [保留的上游 README](docs/README_OFFICIAL.md)
- [ROS2 文档](ros2/README.md)
- [MIT License](LICENSE)
