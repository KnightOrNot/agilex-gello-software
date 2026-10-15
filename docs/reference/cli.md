# CLI 参考

```bash
uv run agilex-gello-software COMMAND [OPTIONS]
```

`gello` 是兼容命令别名；当前项目通过 uv 管理安装与执行。顶层帮助不打开设备。

## 本地读取

```bash
uv run agilex-gello-software read --gello-port /dev/serial/by-id/YOUR_DEVICE
```

| 参数 | 默认值 / 含义 |
| --- | --- |
| `--gello-port PATH` | 必填；键必须在原生 `PORT_CONFIG_MAP` 中 |
| `--baudrate N` | `57600`，正整数 |
| `--json` | stdout 输出 `joints_rad` 与 `gripper`，初始化日志送 stderr |

读取使用本地真实驱动，随后关闭。关节为 rad；夹爪按 open/closed 标定归一化，0 对应开端点、1 对应闭端点，无夹爪时 JSON 为 null。当前 PiPER-X 安装在 controller 根目录使用 `uv run agilex-controller read`，读取应用 TOML 而不是上游表。

中断读取返回 130，参数语法错误返回 2，未知端口或设备失败以非零码结束。

## 上游脚本入口

| 本地命令 | 原始脚本 |
| --- | --- |
| `launch-yaml` | `experiments/launch_yaml.py` |
| `launch-nodes` | `experiments/launch_nodes.py` |
| `camera-server` | `experiments/launch_camera_nodes.py` |
| `camera-client` | `experiments/launch_camera_clients.py` |
| `quick-run` | `experiments/quick_run.py` |
| `run-env` | `experiments/run_env.py` |

参数原样传给脚本，执行时工作目录为 GELLO checkout 根目录，相对配置路径以该目录为基准。不同调用目录使用绝对路径最清楚。命令退出或报错后恢复原 argv/工作目录；不是供多线程应用并发调用的 Python API。

具体选项见 `COMMAND --help`；可选工具可能在帮助前导入其依赖。脚本继续使用原生 `gello.*`，不会自动改用本地驱动或主手 API。`run-env` 的 `start_joints` 恢复上游默认 None；本机旧默认值由 controller 配置管理。

## PiPER-X 应用

跟随、录制与 JS 定位仍在 controller 中：`uv run agilex-controller follow`、`record`、`movejs`。两个一键脚本位于 controller 的 `scripts/`。本库通用上游保存方式与 raw v1 不同，不应替代当前采集流程。
