# 上游兼容与本地差异

上游：[wuphilipp/gello_software](https://github.com/wuphilipp/gello_software)，MIT License。此前保留的上游说明位于 [OFFICIAL.md](OFFICIAL.md)；它经过本 fork 适配，不是当前上游 main 的逐字镜像。

本次整理的目标是沿用现有 GELLO API，减少应用逻辑对 fork 的侵入。没有重新实现上游主手、机器人抽象、YAM/ROS2 或仿真系统。

## 继续保留的适配

- 现有 `src/agilex_gello_software/` 命名空间、uv packaging、基础/可选依赖分组及惰性 CLI。
- `GelloAgent`、`DynamixelRobot`、驱动的显式 close，以及现有通信失败与陈旧读取检查。
- 真实设备模式显式禁用 fake fallback；torque 初始化或起始角度选择失败时释放驱动。
- 通用上游机器人、相机实验、配置生成和 ROS2 代码。
- checkout 资源路径解析、可选依赖分组，以及仿真内置夹爪的归一化适配。

这些差异服务于包装和硬件生命周期，应用仍通过上游的 `GelloAgent(port, dynamixel_config, start_joints)` 与 `act(obs)` 交互。

## 本次迁出的项目内容

- PiPER-X 专用 follow、follow-record、movejs 命令。
- 对应的三个 `experiments/piper_x_*.py` 包装。
- raw episode recorder 及其应用测试。
- Python 端口表中的 FTBM4Z46 本机校准，改由 controller 显式传入。

以上逻辑和配置由 controller 维护。库的 YAM 示例端口、offset 与夹爪端点恢复为上游值；当前安装通过 controller 显式传参保持原有数值。

`configs/yam_auto_generated*.yaml` 等已有生成文件仍可能包含 FTBM4Z46 安装值；它们不会被 controller 自动读取，也不能当作所有设备的通用默认值。

## 同步范围

此前比较的上游基线为 `204f53a64bef89471a1e483b0f874f755fbd2d3a`。本 fork 不是该提交的完整同步版本：上游 ROS2 可配置波特率与发布频率等更新尚未合入，本 fork 的对应路径仍使用固定设置。非 ROS 主手接口和 ROS2 驱动应分别评估，不能用其中一条路径的参数或保护机制推断另一条。

## 后续合并建议

先比较上游 API 和硬件行为，再移植必要的 packaging/lifecycle 改动。将安装设备差异留在应用配置里，将从臂控制与数据存储留在应用层。避免为保持 PiPER-X 工作流而继续修改上游通用环境。
