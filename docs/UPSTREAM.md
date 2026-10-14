# 上游兼容与本地差异

上游：[wuphilipp/gello_software](https://github.com/wuphilipp/gello_software)，MIT License。原项目文档保存在 [README_OFFICIAL.md](README_OFFICIAL.md)。

本次整理的目标是沿用现有 GELLO API，减少应用逻辑对 fork 的侵入。没有重新实现上游主手、机器人抽象、YAM/ROS2 或仿真系统。

## 继续保留的适配

- 现有 `src/agilex_gello_software/` 命名空间、uv packaging、基础/可选依赖分组及惰性 CLI。
- `GelloAgent`、`DynamixelRobot`、驱动的显式 close，以及现有通信失败与陈旧读取检查。
- 真实设备模式显式禁用 fake fallback；torque 初始化或起始角度选择失败时释放驱动。
- 通用上游机器人、相机实验、配置生成和 ROS2 代码。

这些差异服务于包装和硬件生命周期，应用仍通过上游的 `GelloAgent(port, dynamixel_config, start_joints)` 与 `act(obs)` 交互。

## 本次迁出的项目内容

- PiPER-X 专用 follow、follow-record、movejs 命令。
- 对应的三个 `experiments/piper_x_*.py` 包装。
- raw episode recorder 及其应用测试。
- FTBM4Z46 本机的端口与六轴/夹爪校准。

以上逻辑和配置由 controller 维护。库的 YAM 示例端口、offset 与夹爪端点恢复为上游值；当前安装通过 controller 显式传参保持原有数值。

## 后续合并建议

先比较上游 API 和硬件行为，再移植必要的 packaging/lifecycle 改动。将安装设备差异留在应用配置里，将从臂控制与数据存储留在应用层。避免为保持 PiPER-X 工作流而继续修改上游通用环境。
