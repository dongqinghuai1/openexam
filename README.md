# OPENEXAM

OPENEXAM 是一个面向教务运营、在线课堂、考试与财务联动的多角色教育业务平台示例工程。当前仓库已经包含可运行的 Django + DRF 后端、管理后台，以及教师端、学生端、家长端三套可 Docker 部署的 H5 客户端。

## 项目状态

- 后端主干已落地，包含 `users`、`edu`、`classroom`、`exam`、`finance` 五个业务模块。
- 管理后台与教师端、学生端、家长端均已支持 Docker Compose 启动。
- 登录体系已支持邮箱验证码注册与忘记密码重置。
- 管理后台仅允许管理员登录；教师、学生、家长可从统一登录页按角色自动分流到各自端。
- 课堂链路当前可用于教学演示与联调，但不应视为生产级云课堂已完整交付。

## 技术栈

### 后端

- Python 3.12
- Django 4.2+
- Django REST Framework 3.14+
- PostgreSQL 14
- Redis 7
- Gunicorn

### 前端

- 管理后台：Vue 3 + Vite + Element Plus
- 教师端：Taro + React
- 学生端：Taro + React
- 家长端：Taro + React

## 代码入口

- 管理后台：`03_前端开发/01_管理后台`
- 教师端：`03_前端开发/02_教师端`
- 学生端：`03_前端开发/03_学生端`
- 家长端：`03_前端开发/04_家长端`
- 后端：`04_后端开发/03_业务代码`
- Docker 编排：`docker-compose.yml`

## 默认 Docker 部署形态

根目录 `docker-compose.yml` 当前默认启动以下 7 个服务：

- `eduadmin-postgres`
- `eduadmin-redis`
- `eduadmin-backend`
- `eduadmin-frontend`
- `eduadmin-teacher-portal`
- `eduadmin-student-portal`
- `eduadmin-parent-portal`

## 默认访问地址

- 管理后台：`http://127.0.0.1:3000`
- 教师端：`http://127.0.0.1:3001`
- 学生端：`http://127.0.0.1:3002`
- 家长端：`http://127.0.0.1:3003`
- 后端 API：`http://127.0.0.1:8000`
- PostgreSQL：`127.0.0.1:5432`
- Redis：`127.0.0.1:6379`

## 默认账号

- 管理后台：`admin / admin123`
- 教师端：`teacher / teacher123`
- 学生端：`13800000002 / student123`
- 家长端：`13800000003 / parent123`

## 登录与分流

- 管理后台登录页支持：
  - 用户注册
  - 忘记密码
  - 邮箱验证码发送
- 管理后台只允许管理员进入后台。
- 非管理员登录管理后台时，系统会按角色自动跳转：
  - 教师 -> `3001`
  - 学生 -> `3002`
  - 家长 -> `3003`

## 启动方式

### 方式一：Docker

在项目根目录执行：

```bash
docker-compose up -d
```

如果修改了代码并需要重建全部前后端镜像：

```bash
docker-compose up -d --build frontend backend teacher-portal student-portal parent-portal
```

### 方式二：本地开发

后端：

```bash
cd 04_后端开发/03_业务代码
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py init_subjects
python manage.py init_admin
python manage.py init_demo_users
python manage.py runserver 8000
```

管理后台：

```bash
cd 03_前端开发/01_管理后台
npm install
npm run dev
```

三端本地 H5：

- 教师端默认 `3001`
- 学生端默认 `3002`
- 家长端默认 `3003`

```bash
npm install
npm run dev:h5
```

## 邮箱验证码配置

如需启用注册与找回密码，需要给后端配置 SMTP 环境变量：

```bash
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-email@example.com
```

## 文档索引

- 项目概览：`项目概览.md`
- 快速开始：`快速开始.md`
- 部署指南：`部署指南.md`
- 启动验证报告：`06_测试验收/05_验收报告/启动验证报告.md`

## 说明

- 当前仓库最直接的完整运行路径已经是“四端前端 + Django 后端 + PostgreSQL + Redis”。
- 教师端、学生端、家长端当前仍以 H5 演示与业务联调为主，但已支持容器化访问与统一登录分流。
- 如果要做生产部署，仍需补齐正式域名、HTTPS、对象存储、监控告警、密钥管理和更严格的权限审计。
