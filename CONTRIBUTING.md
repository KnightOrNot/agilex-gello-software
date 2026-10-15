# 贡献指南

## 环境与目录边界

使用 Python 3.11、uv 和本仓库独立 `.venv`。先初始化 `third_party/DynamixelSDK`，再 `uv sync --frozen`。解释器与可选依赖见[安装指南](docs/installation.md)。

`gello/`、`experiments/`、`scripts/`、`configs/`、`ros2/`、上游硬件资料和两个第三方版本以 [UPSTREAM.md](docs/UPSTREAM.md) 为准。不要在这些原文件中加入本机校准、改导入名或修复业务行为；新适配写入 `src/agilex_gello_software/`。README 和本地 docs 可以说明 fork，uv/Python 管理文件按项目维护。

| 本地模块 | 责任 |
| --- | --- |
| `agents/gello_agent.py` | 上游 agent 的显式校准与 close 适配 |
| `robots/dynamixel.py` | 注入本地真实驱动，复用上游状态映射与滤波 |
| `dynamixel/driver.py` | 继承上游命令协议，管理真实初始化、反馈时效与关闭 |
| `cli.py`、`commands/read.py` | 本地读取与原脚本转发 |
| `paths.py`、`upstream.py`、`upstream.json` | checkout 资源与离线完整性校验 |

controller 持有主手、客户端和 raw；converter 处理对齐/数据转换。校准从应用经 `DynamixelRobotConfig` 传入，保留上游端口表不变。不要用全局 monkey patch 改写 `gello.*`。

## 风格与回归

本地 Python 使用四空格、公开接口类型标注、`snake_case` 函数/模块和 `PascalCase` 类，运行 Ruff 检查与格式化。测试命名 `tests/test_*.py`，没有覆盖率门槛。

```bash
uv run --frozen pytest
uv run --frozen ruff check src tests
uv run --frozen ruff format --check src tests
uv run --frozen ruff check gello experiments scripts --select E9,F63,F7,F82
uv run --frozen python -m agilex_gello_software.upstream
uv build
```

只格式化 `src/` 和本地 tests，保留原始上游排版。默认 pytest 不收集 `gello/dynamixel/tests/` 的真实串口诊断。通过 fake SDK 的真实读取线程测试失败、超时、符号/单位和资源清理，并与原生 fake robot 对比校准、多圈参考、夹爪和滤波。

硬件初始化不能杀占用串口的进程、改权限或返回 fake 状态继续控制；构造失败和退出需释放已获得资源。测试不移动设备。实机验证需要操作员确认，并明确记录设备、固件、标定及结果。

修改适配或依赖后，在 controller 根目录运行 `uv run --frozen pytest`，验证跟随应用、raw、信号清理和真实 converter 往返；不要把这些软件回归写成实机验收。

## 上游同步与构建

完整性清单固定上游提交、169 个文件和两个第三方提交；README、uv CI、忽略规则是声明过的例外。同步上游时在独立临时 checkout 对比，更新原文件及清单，再验证本地适配。原始 `setup.py`/requirements 保留作上游内容，当前安装以 pyproject 和 uv.lock 为准。

`uv build` 通过 Hatchling 打包两个命名空间。wheel 不含完整实验 checkout；通用脚本需 `GELLO_PROJECT_ROOT` 或 editable checkout。sdist 包含 SDK Python 源与许可，实际开发依赖仍以 uv 的本地 SDK source 为准。

## 提交与文档

优先使用 `fix:`、`refactor:`、`docs:` 等简洁祈使式主题。PR 说明最终行为、上游文件是否变化、依赖和应用兼容性、检查、实机验证状态及 issue。更新本地 README、参考文档、CHANGELOG；上游说明保留在 `docs/OFFICIAL.md`。

独立 checkout 与 controller submodule 不会自动同步。遵循用户先验收再提交的要求；验收后提交本库、发布其版本，再更新 controller gitlink。恢复 DynamixelSDK 时需同时记录 `.gitmodules` 和 `third_party/DynamixelSDK` 的 gitlink，不能把 SDK 源码展开提交进主仓库。

不要提交环境、缓存、数据和构建产物；保留 MIT 及第三方声明。已有生成 YAML/arena 已迁到 `src/agilex_gello_software/configs/legacy/` 仅作历史参考，不能当作当前设备的默认标定。
