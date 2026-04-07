# API接口文档

## 基础信息

- **Base URL**: `http://localhost:8000/api`
- **认证方式**: JWT Bearer Token
- **Content-Type**: `application/json`

---

## 用户模块 `/users/`

### 登录
```
POST /users/login/
Body: { "username": "xxx", "password": "xxx" }
Response: { "token": "...", "refresh_token": "...", "user": {...} }
```

### 刷新Token
```
POST /users/refresh/
Body: { "refresh_token": "xxx" }
Response: { "access_token": "...", "refresh_token": "...", "expires_in": 3600 }
```

### 获取当前用户
```
GET /users/me/
Headers: Authorization: Bearer <token>
```

### 用户列表
```
GET /users/
Query: ?page=1&page_size=10&status=active&search=xxx
```

### 创建用户
```
POST /users/
Body: { "username": "xxx", "password": "xxx", "phone": "xxx", "role_ids": [1,2] }
```

---

## 教务模块 `/edu/`

### 科目
```
GET/POST /edu/subjects/
GET/PUT/DELETE /edu/subjects/{id}/
```

### 课程
```
GET /edu/courses/
POST /edu/courses/
Query: ?subject=1&status=active&search=xxx
```

### 学生
```
GET /edu/students/
POST /edu/students/
GET /edu/students/{id}/hours_accounts/  获取学生课时账户
GET /edu/students/{id}/schedules/      获取学生课表
```

### 教师
```
GET /edu/teachers/
POST /edu/teachers/
GET /edu/teachers/{id}/schedules/       获取教师课表
```

### 班级
```
GET /edu/classes/
POST /edu/classes/
POST /edu/classes/{id}/add_student/     添加学生到班级
DELETE /edu/classes/{id}/remove_student/{student_id}/  移除学生
```

### 排课
```
GET /edu/schedules/
POST /edu/schedules/
GET /edu/schedules/calendar/           日历视图 ?start_date=xxx&end_date=xxx
```

### 课时账户
```
GET /edu/hours/accounts/
GET /edu/hours/flows/                  课时流水
GET /edu/hours/flows/by_student/        按学生查询 ?student_id=xxx
```

### 请假/调课
```
GET /edu/leaves/
POST /edu/leaves/
GET /edu/reschedules/
POST /edu/reschedules/
```

---

## 课堂模块 `/classroom/`

### 会议室
```
GET /classroom/meeting_rooms/
POST /classroom/meeting_rooms/create_meeting/  创建会议 {schedule_id: 1}
GET /classroom/meeting_rooms/{id}/get_token/   获取入会Token
POST /classroom/meeting_rooms/{id}/start_meeting/  开始会议
POST /classroom/meeting_rooms/{id}/end_meeting/    结束会议
```

### 录屏回放
```
GET /classroom/playbacks/
GET /classroom/playbacks/{id}/url/    获取回放地址
```

### 课堂备注
```
GET /classroom/notes/
POST /classroom/notes/
Query: ?schedule=1
```

---

## 考试模块 `/exam/`

### 题目
```
GET /exam/questions/
POST /exam/questions/
Query: ?subject=1&type=single&difficulty=easy
```

### 试卷
```
GET /exam/papers/
POST /exam/papers/
```

### 考试
```
GET /exam/exams/
POST /exam/exams/
POST /exam/exams/{id}/publish/       发布考试
```

### 成绩
```
GET /exam/scores/
GET /exam/scores/by_student/        按学生查询 ?student_id=xxx
```

---

## 财务模块 `/finance/`

### 订单
```
GET /finance/orders/
POST /finance/orders/
POST /finance/orders/{id}/pay/       支付订单
POST /finance/orders/{id}/cancel/   取消订单
GET /finance/orders/statistics/      订单统计 ?start_date=xxx&end_date=xxx
```

### 退款
```
GET /finance/refunds/
POST /finance/refunds/
POST /finance/refunds/{id}/approve/  批准退款
POST /finance/refunds/{id}/reject/   拒绝退款
```

---

## 通用说明

### 分页参数
```
page: 页码 (默认1)
page_size: 每页数量 (默认10)
```

### 筛选参数
```
status: active/inactive
search: 模糊搜索
```

### 排序
```
默认按创建时间 DESC
```

### 错误响应
```json
{ "error": "错误信息" }
```