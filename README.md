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

## 当前状态

- 后端可启动，`/api/v1/health` 正常，Swagger 文档 `/docs` 可访问
- 7 张数据表已通过 Alembic 建表（`alembic upgrade head`）
- **Auth/User 模块已实现**：注册、登录、JWT 鉴权、封禁拦截、资料修改（`/auth/register`、`/auth/login`、`/auth/me`）
- **Item 模块已实现**：图片上传与压缩、发布、列表/搜索/分页、详情、编辑重审、下架、管理员审核
- **Interaction 模块已实现**：商品留言（发布/列表）、收藏/取消收藏、我的收藏
- **Order 模块已实现**：发起订单、我的订单、卖家确认、完成交易、取消订单
- **Admin/举报模块已实现**：提交举报（商品/用户）、我的举报、管理员查看与处理举报工单、用户管理（封禁/解封）
- **管理员申请已实现**：学生提交申请、超级管理员审批；角色分为学生（0）、管理员（1）、超级管理员（2）
- 五个核心业务模块的全部接口均已实现
- 前端页面与路由：首页 / 商品详情 / 登录注册 / 发布 / 个人中心 / 管理后台
- 首页、发布、商品编辑、商品详情（留言/收藏/举报）、我的发布/收藏/订单/举报、资料修改、管理员申请、管理后台审核/举报/用户管理均已接入真实接口

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

## 运行测试

后端提供基于 pytest 的接口自动化测试：

```bash
cd backend
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest -q
```

测试自动创建独立数据库 `CampusMarketTest`，不会影响 `CampusMarket` 演示数据。测试结果与用例明细见 [测试记录.md](测试记录.md)。

## 后续模块顺序

Auth/User（JWT）→ Item（发布/上传/审核）→ Interaction（留言/收藏）→ Order → Admin/举报。
每个模块从 `develop` 拉出 `feature/*` 分支开发，提交信息遵循 `<type>(<scope>): <subject>`。
