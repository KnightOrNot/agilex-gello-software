# 贡献指南

## 责任边界

本库提供主手/电机读取、设备级校准和上游通用框架。PiPER-X 特定的客户端组合、主从方向、跟随启动、退出和 raw 数据录制属于 controller。不要将 controller 或数据转换器作为本库的依赖。

保留的关键模块：

| 路径 | 用途 |
| --- | --- |
| `src/agilex_gello_software/agents/gello_agent.py` | GelloAgent 与 DynamixelRobotConfig |
| `robots/dynamixel.py` | 电机状态、offset/方向、夹爪归一化 |
| `dynamixel/driver.py` | 真实/模拟驱动、通信与读取线程 |
| `commands/read.py` | 库自身的独立只读 CLI |
| `commands/` 其他模块 | 上游通用实验入口 |
| `configs/`、`ros2/`、`experiments/` | 上游配置与实验 |

新项目优先通过 `dynamixel_config=` 传入校准；不要为了一个端口改动上游示例。校准值和面向具体从臂的映射应分开管理。主手夹爪归一化端点与从臂开口含义应由应用明确约定。

## 上游同步

[上游仓库](https://github.com/wuphilipp/gello_software) 的 API 与总体结构是兼容基线。保持已存在的包命名和 uv 适配，避免顺带重写通用模块。具体保留的本地差异见 [UPSTREAM.md](docs/UPSTREAM.md)。

controller 当前通过显式设备配置和 `GelloAgent.act()/close()` 使用库；上游没有 `close()` 的版本需要保留对应最小生命周期扩展。

真实模式不应因初始化失败而返回假状态。初始化中断、torque 设置失败或起始角度选择失败时必须关闭已创建驱动；正常 close 需停止读取线程并释放串口。现有通信错误/陈旧反馈检查应保留。

## 环境与检查

在本仓库目录执行：

```bash
uv sync --frozen
uv run --frozen pytest
uv run --frozen ruff check src tests experiments scripts --select E9,F63,F7,F82
uv build
```

上游文件保留其已有风格；新增测试和独立小模块可用 Ruff 做完整检查，避免混入全库格式化。测试使用模拟驱动，不打开真实串口。

独立 `read` 命令从库的 `PORT_CONFIG_MAP` 查找配置；controller 的 `read` 使用 controller TOML。两者配置来源不同，当前 PiPER-X 安装应使用 controller 入口。

## 多仓库联调

工作区中的独立 `agilex-gello-software/` checkout 与 `agilex-controller/agilex-gello-software/` submodule 是两个工作副本。先测试并发布本库提交，再更新 controller 的 submodule 指针。controller 环境通过本地 editable 路径导入它包含的那份 submodule；修改独立工作副本不会自动改变 controller 的导入内容。

应用集成检查在 controller 根目录执行 `uv run pytest`。raw schema 和转换回归由 controller/converter 维护；库不再包含 PiPER-X raw 录制测试。

## 风格、测试与提交

Python 使用四空格缩进；新公开接口添加类型标注，函数/模块用 `snake_case`，类用 `PascalCase`。保留上游文件已有排版。历史 pre-commit 配置包含 Black、isort、flake8；当前 Python CI 使用上面的 Ruff 基础规则，不要求全库 Ruff 格式化。

测试文件使用 `tests/test_*.py`，没有覆盖率门槛。为读取错误、陈旧反馈、初始化失败与资源释放增加针对性测试；默认 pytest 不收集 `src/` 下需要设备的诊断脚本。真实硬件验证需操作员确认，PR 中写明设备、检查步骤和结果。

提交主题优先使用简洁祈使句和 `fix:`、`refactor:`、`docs:` 等前缀。PR 说明最终行为、上游兼容性、依赖/配置变化、测试结果及硬件验证状态，并关联相关 issue。不要提交 `.venv`、缓存、`*.egg-info`、采集数据或生成的构建产物。

参数或行为变化时同步更新 README、`docs/reference/`、CHANGELOG 和相关测试。保留硬件图片、ROS2 资料和上游版权声明；新增第三方代码需记录来源与许可。
