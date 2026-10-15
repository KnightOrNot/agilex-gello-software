# 上游基线与本地扩展

## 固定版本

- GELLO：[wuphilipp/gello_software](https://github.com/wuphilipp/gello_software/tree/204f53a64bef89471a1e483b0f874f755fbd2d3a)，提交 `204f53a64bef89471a1e483b0f874f755fbd2d3a`。
- DynamixelSDK：`3450c7078917b262d9b36042c15444047aae226e`，Python 元数据 3.7.51。
- MuJoCo Menagerie：`7f0684e0d2f6c9d75174d1a51e4924b7519119f9`，可选初始化。

[OFFICIAL.md](OFFICIAL.md) 保存上游说明，当前 fork 的 uv 开发入口是 [README](../README.md)。

## 原文件保持方式

`gello/` 恢复原始命名空间和全部源文件；`experiments/`、`scripts/`、`configs/`、ROS2、Dockerfile、setup.py、requirements 和硬件资料按固定提交恢复。DynamixelSDK 恢复原始 submodule 来源，不再用 PyPI 4.0.5 代替。ROS2 包括该基线已有的波特率/发布频率更新。

清单 [upstream.json](../src/agilex_gello_software/upstream.json) 记录 169 个原文件的内容哈希/执行位和两个 gitlink。三个原文件有声明过的例外：

| 文件 | 原因 |
| --- | --- |
| `README.md` | 当前 fork 的 uv、架构、使用与开发入口，上游说明放到 OFFICIAL |
| `.github/workflows/pythonapp.yml` | uv、Python 3.11、本地回归和原文件基础 lint |
| `.gitignore` | uv 环境/构建排除，并恢复上游已跟踪 title.png 的可见性 |

pyproject、uv.lock、.python-version、本地 `src/`、tests、贡献/agent 指南、CHANGELOG 和 docs 为本地新增内容，不是对上游业务文件的补丁。

## src 扩展及行为

本地驱动继承上游传输/命令接口，在 src 中实现真实初始化、错误传播、首帧/陈旧读取检查和有界关闭；本地 robot/agent 复用上游状态映射、滤波与 act，提供显式 close。原生模块不被 monkey patch，直接运行上游脚本时仍是原生策略。

通用 CLI 使用原始实验脚本，不再维护改名后的整套副本。旧 fork 的仿真夹爪特殊修改、SpaceMouse 数据类修补和应用 run-env 默认值未写回原文件；这些路径按固定上游实现执行。当前 PiPER-X 主流程不依赖它们。

本机校准在 controller TOML；旧生成文件移到 src 的 `configs/legacy/`。controller 主手导入路径、raw v1 和转换边界保持兼容；安装脚本新增必需 SDK 初始化，两份 uv.lock 同步改用本地 SDK。

## 审计、验收与后续提交

```bash
uv run --frozen python -m agilex_gello_software.upstream
uv run --frozen pytest
```

审计离线比较原文件及已初始化第三方 checkout；可选 Menagerie 未初始化时跳过。它校验当前磁盘内容，不代表原生实验/真实硬件已全部验证。

维护者已确认当前流程运行正常。版本更新时一起记录 `.gitmodules` 与 DynamixelSDK gitlink，不能把第三方源文件作为普通目录展开提交。先验证并发布 GELLO 提交，再提交 controller 的指针与安装/锁文件变化；后续设备路径分别记录验证结果。
