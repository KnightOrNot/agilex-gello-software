# 故障排查

| 现象 | 检查与处理 |
| --- | --- |
| `unknown GELLO port` | 独立 `read` 只识别库端口表。PiPER-X 使用 controller 的 `read`；新应用显式传入校准 |
| 串口被占用 / 权限不足 | 检查稳定的 by-id 路径、`dialout` 和占用进程；先停止持有设备的程序 |
| 无首帧、连续通信失败或状态陈旧 | 检查供电、USB、串联线、ID、波特率。不要用 fake 状态替代真实失败后继续控制 |
| 关节方向或夹爪端点不符 | 核对 offset 单位、sign、端点度数及应用主从映射；先只读验证 |
| `missing optional dependency` | 用 `uv sync --frozen --extra EXTRA` 安装命令所需 extra；外部机器人 SDK 另行准备 |
| 找不到 Menagerie 或配置资源 | 初始化 submodule，或设置 `GELLO_PROJECT_ROOT` / `GELLO_MENAGERIE_ROOT` |
| `follow` / `follow-record` / `movejs` 未知命令 | 使用 controller 统一入口，见 [CLI 参考](cli.md) |

当前非 ROS 驱动的 `get_joints()` 有首帧等待、连续错误与陈旧状态检查；其他读取接口不能据此推定都有相同超时。退出应由持有实例的应用调用 `close()`，不要依赖进程退出回收串口。

报告问题时附 Python/依赖版本、CLI、设备类型、脱敏端口、完整错误和复现步骤，说明使用真实硬件还是模拟驱动。普通回归运行 `uv run --frozen pytest`；不要为排障直接运行源码目录中的硬件测试脚本。
