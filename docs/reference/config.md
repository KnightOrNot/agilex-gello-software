# 设备配置参考

## Python API

`agents/gello_agent.py` 中的 `DynamixelRobotConfig` 提供：

| 字段 | 约定 |
| --- | --- |
| `joint_ids` | 不含夹爪的电机 ID，按应用关节顺序排列 |
| `joint_offsets` | 各关节弧度 offset；数量与 ID 一致 |
| `joint_signs` | 各关节 `1` 或 `-1`；数量与 ID 一致 |
| `gripper_config` | 可省略；`(motor_id, open_deg, closed_deg)`，端点为度 |

基本映射为 `(raw_rad - offset_rad) * sign`。夹爪按两个端点归一化并裁剪到 `[0, 1]`，不能将这两个端点设为相同值。主手端点含义与从臂开口约定可能不同，应由应用确认并映射。

向 `GelloAgent(port=port, dynamixel_config=config, start_joints=reference)` 传入当前设备配置。`start_joints` 是多圈角度选择的参考，不是发送给从臂的运动目标；维度需与机器人状态一致，配置夹爪时包含第七维。使用后调用 `agent.close()`。

独立 `read` 从 `PORT_CONFIG_MAP` 取配置，不读取应用的 TOML。不要为当前 PiPER-X 串口替换库的上游示例；其校准在 controller `config/default.toml` 中。

## YAML 与生成文件

`configs/templates/` 是模板，`configs/references/` 是参考，`configs/yam_auto_generated*.yaml` 是已有生成文件，可能包含安装专用端口和标定值，不能直接视为新设备默认值。生成配置前核对电机 ID、关节方向与实际标定位姿。

`scripts/gello_get_offset.py` 与 `scripts/generate_yam_config.py` 保留上游标定流程。它们会访问硬件；先看 `uv run python scripts/gello_get_offset.py --help` 和[上游操作说明](../OFFICIAL.md)。更改标定后先只读检查，再验证应用映射。

## Checkout 资源路径

| 环境变量 | 用途 |
| --- | --- |
| `GELLO_PROJECT_ROOT` | 仓库根目录；默认从源码 checkout 推断 |
| `GELLO_MENAGERIE_ROOT` | Menagerie 根目录；默认 `third_party/mujoco_menagerie` |

`configs/`、模型和 URDF 依赖 checkout。使用 wheel 或从其他目录运行时显式指定资源路径，不写死个人 home 路径。ROS2 的参数体系见[独立文档](../../ros2/README.md)，不与本库配置自动同步。
