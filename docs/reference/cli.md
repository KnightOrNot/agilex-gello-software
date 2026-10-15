# CLI 参考

在仓库根目录执行 `uv run agilex-gello-software COMMAND [OPTIONS]`；`gello` 是兼容别名。顶层帮助使用惰性导入，不打开设备；部分可选子命令在显示帮助前就需要其依赖。

## 独立读取

```bash
uv run agilex-gello-software read --gello-port /dev/serial/by-id/YOUR_DEVICE
```

将 `YOUR_DEVICE` 替换为已配置在 `PORT_CONFIG_MAP` 中的设备名。

| 参数 | 行为 / 默认值 |
| --- | --- |
| `--gello-port PATH` | 必填；完整路径必须与库端口表键一致 |
| `--baudrate N` | `57600`，正整数 |
| `--json` | stdout 输出 `joints_rad` 和 `gripper`，驱动日志送 stderr |

读取一次后关闭串口，不连接从臂。夹爪按配置的 open/closed 端点归一化为 `0=开端点`、`1=闭端点`；物理含义应由设备标定确认。没有夹爪配置时 JSON 为 `null`。人工中断返回 130，参数语法错误返回 2；未知端口或设备失败以非零码结束。

## 上游通用工具

| 命令 | 用途 / 依赖 |
| --- | --- |
| `launch-yaml` | 根据 `--left-config-path`，可选 `--right-config-path` 启动 YAML 工作流；依赖取决于 `_target_` |
| `launch-nodes` | 机器人 ZMQ 服务；需要对应机器人或仿真依赖 |
| `camera-server` / `camera-client` | 相机服务/显示；需要 `camera` |
| `quick-run` / `run-env` | 上游通用运行流程；通常需要 `full` 及外部硬件库 |

具体参数以 `COMMAND --help` 为准。`experiments/` 保留兼容包装；新脚本优先使用统一 CLI。YAML 中可能指定真实机器人，执行前检查目标设备与控制参数。

## PiPER-X 迁移入口

在 controller 根目录运行 `uv run agilex-controller follow`、`record` 或 `movejs`。本库不再提供 PiPER-X `follow`、`follow-record` 和 `movejs` 命令，通用上游保存格式也不等于 controller 的 raw v1 格式。
