# 安装指南

## Python 与 uv

当前项目使用 Python 3.11 和 uv；上游安装说明保留在 [OFFICIAL.md](OFFICIAL.md)，日常开发按本文执行。新 checkout 在仓库根目录初始化必需 SDK：

```bash
git submodule update --init third_party/DynamixelSDK
uv sync --frozen
uv run agilex-gello-software --help
```

SDK 固定上游提交 `3450c7078917b262d9b36042c15444047aae226e`，其 Python 元数据版本为 3.7.51。`tool.uv.sources` 安装该 checkout 的 `python/`，不再使用 PyPI 4.0.5 替代。不要修改第三方源码或手动混装另一版本。

controller 开发安装可使用 `./scripts/setup.sh --skip-system --skip-submodules` 保留本地改动；使用该选项前需确保 SDK 已初始化。新 clone 按上述 submodule 流程获取固定版本。

由 pyenv 管理解释器时，可先选好 3.11，再显式传给 uv：

```bash
UV_NO_MANAGED_PYTHON=1 uv sync --frozen --python "$(pyenv which python)"
```

无需激活虚拟环境。controller 与本库独立环境都会安装同一份本地 SDK Python 源；SDK 服务和 converter 仍使用各自环境。

## 串口与只读检查

Linux 下先核对 `/dev/serial/by-id/`、电机 ID、波特率和供电。Ubuntu 用户需要时加入 `dialout`，注销并重新登录。不要让多个进程同时打开同一 GELLO 串口。

独立读取要求端口已在上游端口表中；当前 PiPER-X 校准来自 controller TOML，应在 controller 根目录执行 `uv run agilex-controller read`。校准与从臂方向不是同一层，详见[配置参考](reference/config.md)。

## 可选上游功能

```bash
uv sync --frozen --extra simulation
```

可选 extra 为 `simulation`、`robots`、`camera`、`full`。需要多个 extra 时在一次同步中分别传入；后续只同步基础环境可能移除可选包。仿真模型另外初始化：

```bash
git submodule update --init third_party/mujoco_menagerie
```

普通主手读取不需要这些模型。原生脚本继续从 checkout 根目录解析相对配置、模型和 URDF；通过本地 CLI 启动时自动切换根目录。wheel 中的库可单独导入，但通用实验还需 checkout，用 `GELLO_PROJECT_ROOT` 指定。

I2RT、Polymetis、ROS2、图形环境和设备驱动不由基础包自动配置。按[上游说明](OFFICIAL.md)准备并验证；恢复上游源码不等于完成所有真实硬件联调。
