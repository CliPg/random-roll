# 随机点名系统 (random-roll)

这是一个用于课堂点名与积分管理的轻量级系统，包含后端（Python + SQLite）和前端（Uni-app / Vue）两个部分，支持通过 Excel 导入学生名单、按积分概率随机点名、积分导出与排行榜等功能。

## 简介

- 功能：学生名单导入/导出、随机点名（按积分概率调节命中率）、顺序点名、提交点名结果并更新积分、积分排行榜展示。
- 目标用户：教师/助教用于课堂点名、课堂互动及积分管理。

## 技术栈

- 后端：Python 3.8+、Peewee（SQLite ORM）、基于自制的轻量 API（见 `roll-backend`）
- 数据库：SQLite（轻量便携，保存在 `roll-backend/database/`）
- 前端：Uni-app + Vue 3（在 `roll-frontend`，可编译为 H5 / 小程序 / App 等多端）
- 工具与格式：Excel（通过 `xlsx` 库导入/导出）、简单的命令行脚本用于初始化

## 亮点

- 概率点名：使用积分反向概率（积分越高，被点到的概率越低）实现更公平的抽查。
- Excel 导入/导出：支持将学生名单和积分表通过 Excel 文件导入/导出，便于教师管理与备份。
- 多端前端：基于 Uni-app，前端可同时发布为 H5、小程序或原生 App。
- 极简后端：使用 SQLite + Peewee，零运维，适合小班/课程场景快速部署。

## 项目结构（简要）

- `roll-backend/`：后端服务代码，含 API、数据库脚本和运行脚本（`run.sh`）。
- `roll-frontend/`：Uni-app 前端源码，使用 Vue 3 + TypeScript。可在多平台运行。
- `students/`、`points/`、`roll/`：封装了导入/导出、积分排行、点名逻辑的脚本模块。
- `frontend-demo/`：简单静态预览页面 `preview.html`（用于快速查看 UI 效果）。

## 使用方法

以下说明基于 macOS / zsh。请在项目根目录运行命令。

### 后端（快速启动）

1. 进入后端目录并创建虚拟环境：

```bash
cd roll-backend
python3 -m venv .venv
source .venv/bin/activate
```

2. 安装依赖：

```bash
# 如果仓库提供 requirements.txt：
pip install -r requirements.txt || true

# 使用 pyproject.toml 中定义的依赖（或至少安装 peewee）：
pip install -e . || pip install peewee
```

3. 初始化数据库（如需要）：

```bash
python3 database/create.py
```

4. 启动服务：

```bash
./run.sh
# 或直接：
python3 -m server
```

服务启动后，默认会监听在配置的端口（参见 `roll-backend/server` 内的配置）。

常用后端接口（示例）：

- POST /students/import —— 从 Excel 导入学生名单
- GET /students/list —— 获取学生列表
- GET /rollcall/random —— 按概率随机点名
- GET /rollcall/sequential —— 顺序点名
- POST /rollcall/result —— 提交点名结果并更新积分
- GET /points/rank —— 获取积分排行榜

（可在 `roll-backend/server/verapi.py` / `roll-backend/server/verdata.py` 中查看实现与路由）

### 前端（开发/预览）

1. 进入前端目录并安装依赖（使用 pnpm / npm 均可）：

```bash
cd ../roll-frontend
pnpm install # 或 npm install
```

2. 运行开发模式预览：

```bash
pnpm run dev:mp-weixin
```


### 导入学生（示例流程）

1. 在前端「导入」界面选择 Excel 文件并上传到后端 `POST /students/import`。
2. 后端解析并存储学生信息到 SQLite，返回导入结果。
3. 可通过 `GET /students/list` 验证数据。

如果需要在命令行直接导入（批量）：

```bash
python3 students/import.py path/to/students.xlsx
```

（具体脚本参数请查看 `students/import.py` 源码）


## 备注与贡献

- 本项目适合小规模课堂使用；如果用于生产或并发场景，建议换用服务端数据库（Postgres/MySQL）并加入认证与权限控制。
- 欢迎提交 Issue 或 PR，提报 bug 或改进建议。





