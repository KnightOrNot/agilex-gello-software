# 设备配置参考

## 本地 Python API

使用 `agilex_gello_software.agents.gello_agent.DynamixelRobotConfig`，它继承原生配置并让 `make_robot()` 创建本地生命周期适配。也可把原生配置传给本地 `GelloAgent`，由入口转换。

| 字段 | 约定 |
| --- | --- |
| `joint_ids` | 不含夹爪的电机 ID，按关节顺序排列 |
| `joint_offsets` | 弧度 offset，数量与 ID 一致 |
| `joint_signs` | 每个关节为 +1 或 -1 |
| `gripper_config` | 可为 None；`(motor_id, open_deg, closed_deg)`，端点单位度 |

状态映射、夹爪归一化与 0.99 指数滤波复用上游实现。夹爪两端点不能相同，物理方向由标定决定。主手端点与 SDK 从臂 `0=闭/1=开` 的关系应由应用确认；当前 controller 保留既有直接传递规则。

`start_joints` 是多圈角度参考，不是从臂运动目标；维度需与完整主手状态一致，有夹爪时包含夹爪维。本地 API 保留原有对齐结果，使用后调用 `close()`。

## 上游配置与本机配置

原生 `gello.agents.gello_agent.PORT_CONFIG_MAP` 和 `configs/` 保持上游原值。本地 `read` 使用该端口表；controller 使用自己的 `config/default.toml`。不要为 FTBM4Z46 改写上游 YAM 示例。

此前生成的本机 YAML/arena 保存到 `src/agilex_gello_software/configs/legacy/`，仅供追溯，内部旧命名空间不保证可直接运行。新实验应从上游模板重新生成并核对硬件。标定工具位于原始 `scripts/`，直接访问硬件，按 [OFFICIAL.md](../OFFICIAL.md) 操作。

## 依赖与路径

SDK 源为 `third_party/DynamixelSDK/python`，确切提交见 [UPSTREAM.md](../UPSTREAM.md)。Python 3.11、可选依赖和两个包的构建由 pyproject/uv.lock 管理，原始 setup.py 不决定当前 uv 元数据。

`GELLO_PROJECT_ROOT` 指定包含 `gello/` 和 `experiments/` 的 checkout，默认从 editable 源码推断。本地 CLI 切换到此目录运行上游脚本。原生脚本并不自动读取旧 fork 的 `GELLO_MENAGERIE_ROOT`；模型默认仍放在 `third_party/mujoco_menagerie`，遵循上游路径约定。
