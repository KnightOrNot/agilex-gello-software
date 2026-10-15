# 故障排查

| 现象 | 检查与处理 |
| --- | --- |
| 找不到本地 DynamixelSDK source | 初始化 `third_party/DynamixelSDK` 后重新 `uv sync --frozen`；当前验收工作树已检出 |
| `import gello` 失败 | 重新同步当前 pyproject；构建必须同时提供 gello 与本地 src，不能只拷贝 src |
| 独立 read 提示未知串口 | 它使用上游表；PiPER-X 用 controller 的 read，或在应用中显式传校准 |
| 串口忙、无权限、首次读取超时 | 停止占用程序，检查 dialout、供电、接线、ID 与波特率；本地入口不自动杀进程/改权限 |
| 反馈陈旧、连续失败或字段不完整 | 本地适配拒绝继续返回缓存，排查真实通信，不要用 fake fallback 掩盖失败 |
| 上游完整性校验失败 | 按报错文件对比固定基线；业务修改移到 src，升级上游需同时更新清单 |
| 通用脚本缺依赖或模型 | 同步相应 extra、初始化 Menagerie，并按上游说明准备外部 SDK |
| 通用脚本找不到相对 YAML/URDF | CLI 在 GELLO checkout 根目录执行，传正确相对路径或绝对路径 |
| close 不存在或仍有原生 fake 行为 | 检查导入是否为本地 `agilex_gello_software.*`；原生 `gello.*` 没有被全局修改 |

## 验证依赖来源

在本库目录执行：

```bash
uv run python -c "import dynamixel_sdk; from importlib.metadata import version; print(version('dynamixel-sdk')); print(dynamixel_sdk.__file__)"
uv run python -m agilex_gello_software.upstream
```

SDK 版本应为 3.7.51，来源为本 checkout 的 `third_party/DynamixelSDK/python/src/`。controller 环境也应解析到同一份 SDK。不要手动在某个 `.venv` 中替换版本后继续使用旧锁文件。

原生上游驱动保留原行为；本地保护只作用于本地入口。报告问题时附提交/待验收状态、导入路径、CLI、依赖来源、标定和完整错误。默认 pytest 不访问设备；实机验证与软件回归分开记录。
