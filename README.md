# OPENEXAM

OPENEXAM 是一个面向教务运营、在线课堂、考试与财务联动的多角色业务平台示例工程。当前仓库已经包含可运行的 Django + DRF 后端、可部署的管理后台，以及教师端、学生端、家长端三套 Taro 客户端源码。

## 项目状态

- 后端主干已落地，包含用户权限、教务、课堂、考试、财务 5 个业务模块。
- 管理后台可本地开发、可 Docker 部署，已完成一轮联调与启动验证。
- 教师端、学生端、家长端已具备独立工程和 H5/小程序构建脚本，当前定位是演示版客户端，不在根目录 Docker Compose 的默认部署范围内。
- 课堂相关能力目前以 Mock/演示链路为主，不应视为真实云会议能力已完整接入。

## 技术栈

### 后端

- Python 3.12 容器运行时
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

## 后端模块

- `users`：登录、角色、菜单、通知、操作日志、Dashboard 数据
- `edu`：科目、课程、学生、教师、班级、排课、请假、调课、课时账户与流水
- `classroom`：会议室、课堂记录、录制任务、回放文件、课堂笔记
- `exam`：题目、试卷、考试、成绩记录
- `finance`：订单、退款、统计相关能力

## 默认部署形态

根目录 `docker-compose.yml` 当前默认启动以下 4 个服务：

- `eduadmin-postgres`
- `eduadmin-redis`
- `eduadmin-backend`
- `eduadmin-frontend`

其中 `eduadmin-frontend` 指的是管理后台，不包含教师端、学生端、家长端。

## 快速访问

Docker 启动后默认访问地址：

- 管理后台：`http://127.0.0.1:3000`
- 后端 API：`http://127.0.0.1:8000`
- PostgreSQL：`127.0.0.1:5432`
- Redis：`127.0.0.1:6379`

## 默认账号

后端初始化命令会创建以下演示账号：

- 管理后台：`admin / admin123`
- 教师端：`teacher / teacher123`
- 学生端：`13800000002 / student123`
- 家长端：`13800000003 / parent123`

## 启动方式

### 方式一：Docker

在项目根目录执行：

```bash
docker-compose up -d
```

如果修改了管理后台或后端代码并需要重建镜像：

```bash
docker-compose up -d --build frontend backend
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

教师端、学生端、家长端均支持类似的 Taro 命令：

```bash
npm install
npm run dev:h5
```

## 文档索引

- 项目概览：`项目概览.md`
- 快速开始：`快速开始.md`
- 部署指南：`部署指南.md`
- 启动验证报告：`06_测试验收/05_验收报告/启动验证报告.md`
- 系统架构：`02_产品设计调研/03_业务流程图/系统整体架构与模块设计.md`

## 说明

- 本仓库当前最完整、最直接的运行路径是“Django 后端 + 管理后台 + PostgreSQL + Redis”。
- 用户端三套客户端已具备源码和构建脚本，但文档中不再将它们描述为与管理后台同等完成度的正式交付物。
- 如果要做生产部署，仍需补齐环境隔离、密钥管理、监控告警、对象存储、真实第三方服务接入与安全审计等内容。
