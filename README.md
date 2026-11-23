# 校园闲置物二手置换平台

课程设计项目。设计文档见 [软件设计说明书.md](软件设计说明书.md)，协作流程见 [Git 协作规范.md](Git%20协作规范.md)。

## 目录结构

```
backend/            FastAPI 后端
  app/
    routers/        路由层（Controller）
    services/       业务逻辑层
    models/         SQLAlchemy 模型（6 张表）
    schemas/        Pydantic 校验模型
    core/           配置 / JWT / 工具
    db/             数据库会话
  static/uploads/   图片上传目录（/uploads 前缀对外访问）
frontend/           Vue3 + Vite + Element Plus 前端
resource/           设计图（E-R 图、UML 类图、流转图）
tools/              图表生成脚本
```

## 当前状态（骨架阶段）

- 后端可启动，`/api/v1/health` 正常，Swagger 文档 `/docs` 可访问
- 6 张数据表模型、各模块路由与 Schema 已定义
- 业务接口暂为占位实现，统一返回 `501 {detail: "xxx 尚未实现"}`
- 前端页面与路由已搭好：首页 / 商品详情 / 登录 / 发布 / 个人中心 / 管理后台
- 首页使用本地 mock 数据，接口接通后替换

## 启动后端

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env        # 按本机 MySQL 账号密码修改 DATABASE_URL
.venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

- 健康检查：<http://127.0.0.1:8000/api/v1/health>
- 接口文档：<http://127.0.0.1:8000/docs>

## 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 <http://127.0.0.1:5173>，开发服务器已把 `/api`、`/uploads` 代理到 `127.0.0.1:8000`。

## 后续模块顺序

Auth/User（JWT）→ Item（发布/上传/审核）→ Interaction（留言/收藏）→ Order → Admin/举报。
每个模块从 `develop` 拉出 `feature/*` 分支开发，提交信息遵循 `<type>(<scope>): <subject>`。
