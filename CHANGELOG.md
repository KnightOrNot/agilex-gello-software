# Changelog

## Unreleased

- 按 controller 文档结构整理安装、架构、CLI、设备配置、排障与贡献指南，保留上游说明和硬件资料。
- 补充 agent 开发约束、许可来源与多仓库提交流程。

## 0.1.0

以下记录现有实现，不表示新增发布 tag。

- 使用 `src/agilex_gello_software/`、Python 3.11、uv 和统一惰性 CLI，保留 `gello` 命令别名。
- 分离基础、相机、机器人和仿真依赖，提供独立 `read` 命令。
- 增加真实驱动读取错误/陈旧状态检查，以及显式关闭和初始化失败清理。
- 将 PiPER-X 客户端、JS 定位、跟随和 raw 录制迁入 controller；本机校准通过应用配置传入。
- 保留通用机器人、YAM、ROS2、相机实验和仿真工具；具体上游差异见 [UPSTREAM.md](docs/UPSTREAM.md)。
