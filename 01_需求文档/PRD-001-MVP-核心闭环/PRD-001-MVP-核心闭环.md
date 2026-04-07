# PRD-001: MVP核心闭环

## 1. 文档信息

| 项目 | 内容 |
|------|------|
| 文档编号 | PRD-001 |
| 文档名称 | MVP核心闭环 |
| 版本号 | V1.0 |
| 创建日期 | 2026-04-07 |
| 状态 | 开发中 |
| 优先级 | P0 (最高) |

## 2. 需求概述

### 2.1 核心目标

实现"能招生建档、能排课、能上课、能录屏、能扣课时、能收款"的核心业务闭环。

### 2.2 业务范围

| 模块 | 功能点 | 优先级 |
|------|--------|--------|
| 用户权限 | 登录/注册/角色/权限 | P0 |
| 学生管理 | 建档/CRUD/状态 | P0 |
| 教师管理 | 建档/CRUD/擅长 | P0 |
| 课程管理 | CRUD/章节/课时 | P0 |
| 班级管理 | 创建/分班/绑定 | P0 |
| 排课管理 | 日历排课/冲突检测/调课 | P0 |
| 在线课堂 | 腾讯会议接入/发起/进入 | P0 |
| 录屏回放 | 自动录制/回放/下载 | P0 |
| 课时管理 | 账户/流水/扣减 | P0 |
| 订单管理 | 创建/支付/状态 | P0 |
| 通知 | 短信/模板消息 | P1 |

### 2.3 用户角色

| 角色 | 描述 | 权限范围 |
|------|------|----------|
| 超级管理员/校长 | 全局管理 | 全部模块 |
| 教务管理员 | 教务业务 | 教务模块 |
| 教师 | 教学人员 | 课堂/学生 |
| 学生 | 学员 | 个人学习 |
| 财务 | 财务数据 | 财务模块 |

### 2.4 技术架构

| 层级 | 技术选型 |
|------|----------|
| 前端管理后台 | Vue3 + Element Plus |
| 课堂端 | Taro (React) |
| 后端 | Python/Django + DRF |
| 数据库 | PostgreSQL |
| RTC | 腾讯会议 SDK |
| 缓存 | Redis |

---

## 3. 功能需求

### 3.1 用户权限模块

#### 3.1.1 用户账号

| 功能 | 描述 | API依赖 |
|------|------|--------|
| 注册 | 手机号/邮箱注册 | auth/register |
| 登录 | JWT登录(用户名/密码/验证码) | auth/login |
| 登出 | Token失效 | auth/logout |
| 刷新Token | 续期JWT | auth/refresh |
| 重置密码 | 短信验证码重置 | auth/password/reset |

#### 3.1.2 角色权限

| 功能 | 描述 | 字段 |
|------|------|------|
| 角色管理 | 创建/编辑/删除角色 | role, permissions, status |
| 菜单权限 | 动态菜单渲染 | menu_id, parent_id |
| 数据权限 | 部门/班级隔离 | data_scope |
| 接口权限 | API级别控制 | api_path, method |

**数据结构**：

```python
class Role(models.Model):
    name = models.CharField(max_length=50)  # 角色名称
    code = models.CharField(max_length=20, unique=True)  # 角色编码
    description = models.TextField(blank=True)  # 描述
    permissions = models.ManyToManyField('Permission')  # 权限
    status = models.BooleanField(default=True)  # 状态
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Permission(models.Model):
    name = models.CharField(max_length=50)  # 权限名称
    code = models.CharField(max_length=50, unique=True)  # 权限编码
    menu = models.ForeignKey('Menu', on_delete=models.SET_NULL, null=True)  # 菜单
    api_path = models.CharField(max_length=100, blank=True)  # API路径
    method = models.CharField(max_length=10, choices=[('GET','GET'),('POST','POST'),('PUT','PUT'),('DELETE','DELETE')])

class Menu(models.Model):
    name = models.CharField(max_length=50)
    path = models.CharField(max_length=100)
    component = models.CharField(max_length=100)
    icon = models.CharField(max_length=50)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    sort = models.IntegerField(default=0)
    visible = models.BooleanField(default=True)
```

---

### 3.2 学生管理模块

#### 3.2.1 学生档案

| 功能 | 描述 | 字段 |
|------|------|------|
| 创建学生 | 新增学生档案 | 姓名/手机/性别/出生/年级/学校/联系人 |
| 编辑学生 | 修改学生信息 | 同创建 |
| 删除学生 | 软删(状态=已删除) | status='deleted' |
| 查询学生 | 列表/详情/搜索 | 分页/条件/排序 |
| 导入学生 | Excel批量导入 | phone, name |

**数据结构**：

```python
class Student(models.Model):
    name = models.CharField(max_length=50)  # 姓名
    phone = models.CharField(max_length=20, unique=True)  # 手机号
    avatar = models.CharField(max_length=500, blank=True)  # 头像URL
    gender = models.CharField(max_length=10, choices=[('male','男'),('female','女')])
    birthday = models.DateField(null=True)  # 出生日期
    grade = models.CharField(max_length=20)  # 年级
    school = models.CharField(max_length=100, blank=True)  # 学校
    parent_name = models.CharField(max_length=50)  # 家长姓名
    parent_phone = models.CharField(max_length=20)  # 家长手机
    status = models.CharField(max_length=20, default='active')  # active/inactive/graduated/deleted
    enrollment_date = models.DateField()  # 入学日期
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 3.2.2 状态管理

| 状态 | 描述 | 流转 |
|------|------|------|
| 在读 | 正常学习 | default |
| 休学 | 暂停学习 | 申请→审批 |
| 退学 | 离开机构 | 申请→退款→完成 |
| 毕业 | 完成课程 | 课时用完/课程结束 |

---

### 3.3 教师管理模块

#### 3.3.1 教师档案

| 功能 | 描述 | 字段 |
|------|------|------|
| 创建教师 | 新增教师档案 | 姓名/手机/性别/学历/擅长/入职 |
| 编辑教师 | 修改教师信息 | 同创建 |
| 删除教师 | 软删(状态=已离职) | status='resigned' |
| 查询教师 | 列表/详情/搜索 | 分页/条件/排序 |
| 擅长科目 | 标记教师擅长科目 | subjects |

**数据结构**：

```python
class Teacher(models.Model):
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, unique=True)
    avatar = models.CharField(max_length=500, blank=True)
    gender = models.CharField(max_length=10, choices=[('male','男'),('female','女')])
    birthday = models.DateField(null=True)
    education = models.CharField(max_length=20)  # 学历
    major = models.CharField(max_length=50)  # 专业
    certification = models.CharField(max_length=50, blank=True)  # 证书
    subjects = models.ManyToManyField('Subject')  # 擅长科目
    status = models.CharField(max_length=20, default='active')  # active/resigned
    hire_date = models.DateField()  # 入职日期
    salary_type = models.CharField(max_length=20)  # 按课时/固定
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 3.3.2 教师状态

| 状态 | 描述 | 流转 |
|------|------|------|
| 在职 | 正常教学 | default |
| 停课 | 暂停教学 | 申请→审批 |
| 离职 | 离开机构 | 申请→结算→完成 |

---

### 3.4 课程管理模块

#### 3.4.1 课程定义

| 功能 | 描述 | 字段 |
|------|------|------|
| 创建课程 | 新增课程 | 名称/科目/描述/总课时/价格 |
| 编辑课程 | 修改课程信息 | 同创建 |
| 删除课程 | 软删 | status='archived' |
| 章节管理 | 大章节/小结 | chapter->sections |

**数据结构**：

```python
class Course(models.Model):
    name = models.CharField(max_length=100)  # 课程名称
    code = models.CharField(max_length=20, unique=True)  # 课程编码
    subject = models.ForeignKey('Subject', on_delete=models.PROTECT)  # 科目
    description = models.TextField(blank=True)  # 课程描述
    total_hours = models.IntegerField()  # 总课时
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 价格
    duration = models.IntegerField(default=90)  # 单次课时长(分钟)
    status = models.CharField(max_length=20, default='active')  # active/archived
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Chapter(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # 章节名称
    sort = models.IntegerField(default=0)  # 排序

class Section(models.Model):
    chapter = models.ForeignKey('Chapter', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # 小结名称
    content = models.TextField(blank=True)  # 内容
    sort = models.IntegerField(default=0)
```

#### 3.4.2 科目

```python
class Subject(models.Model):
    name = models.CharField(max_length=50)  # 科目名
    code = models.CharField(max_length=20, unique=True)  # 编码
    sort = models.IntegerField(default=0)
    status = models.BooleanField(default=True)

class CoursePackage(models.Model):
    name = models.CharField(max_length=100)  # 套餐名
    courses = models.ManyToManyField('Course')  # 包含课程
    hours = models.IntegerField()  # 总课时
    price = models.DecimalField(max_digits=10, decimal_places=2)
    valid_days = models.IntegerField(default=365)  # 有效期(天)
```

---

### 3.5 班级管理模块

#### 3.5.1 班级

| 功能 | 描述 | 字段 |
|------|------|------|
| 创建班级 | 新增班级 | 名称/课程/教室/人数上限 |
| 编辑班级 | 修改班级信息 | 同创建 |
| 删除班级 | 软删 | status='closed' |
| 学生分班 | 添加学生到班级 | class_student |
| 教师绑定 | 分配授课教师 | class_teacher |

**数据结构**：

```python
class Class(models.Model):
    name = models.CharField(max_length=100)  # 班级名称
    code = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey('Course', on_delete=models.PROTECT)
    teacher = models.ForeignKey('Teacher', on_delete=models.PROTECT, related_name='classes')
    max_students = models.IntegerField(default=20)  # 最大人数
    status = models.CharField(max_length=20, default='open')  # open/closed
    start_date = models.DateField()  # 开班日期
    end_date = models.DateField(null=True)  # 结课日期
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ClassStudent(models.Model):
    edu_class = models.ForeignKey('Class', on_delete=models.CASCADE)
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    join_date = models.DateField()  # 入班日期
    status = models.CharField(max_length=20, default='studying')  # studying/graduated/removed
    created_at = models.DateTimeField(auto_now_add=True)
```

---

### 3.6 排课管理模块

#### 3.6.1 排课

| 功能 | 描述 | 字段 |
|------|------|------|
| 创建课次 | 新增排课 | 班级/教师/日期/时段/教室 |
| 编辑课次 | 修改排课信息 | 同创建 |
| 删除课次 | 取消排课 | status='cancelled' |
| 冲突检测 | 检测教师/教室冲突 | 自动检测 |
| 课表视图 | 日/周/月视图 | calendar |

**数据结构**：

```python
class Schedule(models.Model):
    edu_class = models.ForeignKey('Class', on_delete=models.CASCADE)
    teacher = models.ForeignKey('Teacher', on_delete=models.PROTECT)
    course = models.ForeignKey('Course', on_delete=models.PROTECT)
    date = models.DateField()  # 上课日期
    start_time = models.TimeField()  # 开始时间
    end_time = models.TimeField()  # 结束时间
    room = models.CharField(max_length=50, blank=True)  # 教室/会议室
    status = models.CharField(max_length=20, default='scheduled')  # scheduled/cancelled/completed
    note = models.TextField(blank=True)  # 备注
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 3.6.2 调课

| 功能 | 描述 | 字段 |
|------|------|------|
| 调课申请 | 修改课次时间/教师 | 原课次/新时间/新教师 |
| 补课 | 新增补课课次 | 原课次/新时间 |
| 请假 | 学生/教师请假 | applicant/type/reason |

**数据结构**：

```python
class RescheduleRecord(models.Model):
    original_schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE, related_name='original')
    new_schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE, related_name='new', null=True)
    type = models.CharField(max_length=20)  # adjust/reschedule/supplement
    reason = models.TextField()  # 调课原因
    status = models.CharField(max_length=20, default='pending')  # pending/approved/rejected
    applicant = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    approver = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='approved')
    created_at = models.DateTimeField(auto_now_add=True)

class LeaveRecord(models.Model):
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE)
    applicant = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)  # 教师/学生
    type = models.CharField(max_length=20)  # student/teacher
    reason = models.TextField()
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
```

---

### 3.7 在线课堂模块 (腾讯会议)

#### 3.7.1 课堂管理

| 功能 | 描述 | 字段 |
|------|------|------|
| 创建课堂 | 发起腾讯会议 | 课次/会议主题 |
| 进入课堂 | 获取会议Token | user/schedule |
| 结束课堂 | 结束会议 | meeting_id |
| 课堂状态 | 实时状态 | pending/ongoing/ended |

**数据结构**：

```python
class MeetingRoom(models.Model):
    schedule = models.OneToOneField('Schedule', on_delete=models.CASCADE)
    meeting_id = models.CharField(max_length=50)  # 腾讯会议ID
    meeting_password = models.CharField(max_length=20)  # 会议密码
    join_url = models.CharField(max_length=500)  # 加入链接
    host_key = models.CharField(max_length=20)  # 主持人密钥
    status = models.CharField(max_length=20, default='pending')  # pending/ongoing/ended
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class MeetingRecord(models.Model):
    meeting_room = models.ForeignKey('MeetingRoom', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    join_time = models.DateTimeField()
    leave_time = models.DateTimeField(null=True)
    duration = models.IntegerField(default=0)  # 参会时长(秒)
    role = models.CharField(max_length=20)  # host/participant
```

#### 3.7.2 腾讯会议API对接

**核心API列表**：

| API | 说明 | SDK依赖 |
|------|------|--------|
| CreateMeeting | 创建会议 | wemeet-openapi-sdk-python |
| GetMeetingInfo | 获取会议信息 | wemeet-openapi-sdk-python |
| EndMeeting | 结束会议 | wemeet-openapi-sdk-sdk |
| GetJoinUrl | 获取入会链接 | wemeet-openapi-sdk-python |

**集成代码示例**：

```python
import wemeet_openapi
import random
import time

class TencentMeetingService:
    def __init__(self):
        self.client = wemeet_openapi.Client(
            app_id=settings.TENCENT_APP_ID,
            sdk_id=settings.TENCENT_SDK_ID,
            secret_id=settings.TENCENT_SECRET_ID,
            secret_key=settings.TENCENT_SECRET_KEY
        )

    def create_meeting(self, subject, start_time, end_time, user_id):
        """创建腾讯会议"""
        request = wemeet_openapi.ApiV1MeetingsPostRequest(
            body=wemeet_openapi.V1MeetingsPostRequest(
                instanceid=2,
                meeting_type=0,
                subject=subject,
                type=1,
                userid=user_id,
                start_time=start_time,
                end_time=end_time
            )
        )
        authenticator = wemeet_openapi.JWTAuthenticator(
            nonce=random.randrange(0, 2 ** 64),
            timestamp=str(int(time.time()))
        ).options_build()
        return self.client.meetings_api.v1_meetings_post(request, [authenticator])

    def get_meeting_token(self, meeting_id, user_id, user_name):
        """获取入会Token"""
        # 使用TRTC SDK生成用户签名
        pass
```

---

### 3.8 录屏回放模块

#### 3.8.1 录制

| 功能 | 描述 | 字段 |
|------|------|------|
| 自动录制 | 课次开始时自动启动 | 腾讯会议录制 |
| 录制状态 | 录制中/转码中/已完成 | 腾讯云自动化 |
| 回放文件 | 录屏文件地址 | OSS/COS |

**数据结构**：

```python
class RecordingTask(models.Model):
    meeting_room = models.ForeignKey('MeetingRoom', on_delete=models.CASCADE)
    record_id = models.CharField(max_length=50)  # 腾讯会议录制ID
    status = models.CharField(max_length=20, default='processing')  # processing/transcoding/ready
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PlaybackFile(models.Model):
    recording_task = models.ForeignKey('RecordingTask', on_delete=models.CASCADE)
    file_url = models.CharField(max_length=500)  # 回放地址
    file_size = models.BigIntegerField()  # 文件大小
    duration = models.IntegerField()  # 时长(秒)
    status = models.CharField(max_length=20, default='pending')  # pending/ready
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 3.8.2 回放权限

| 角色 | 权限 |
|------|------|
| ���生 | 课后可看(可配置) |
| 教师 | 随时查看 |
| 管理员 | 随时查看 |

---

### 3.9 课时管理模块

#### 3.9.1 课时账户

| 功能 | 描述 | 字段 |
|------|------|------|
| 账户创建 | 购买课程后创建 | student/course |
| 课时查询 | 剩余/已用/总课时 | 统计API |
| 赠送课时 | 赠送/活动课时 | type='gift' |
| 冻结课时 | 请假冻结 | type='frozen' |

**数据结构**：

```python
class StudentHoursAccount(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.PROTECT)
    total_hours = models.DecimalField(max_digits=10, decimal_places=1)  # 总课时
    used_hours = models.DecimalField(max_digits=10, decimal_places=1, default=0)  # 已用
    frozen_hours = models.DecimalField(max_digits=10, decimal_places=1, default=0)  # 冻结
    gift_hours = models.DecimalField(max_digits=10, decimal_places=1, default=0)  # 赠送
    status = models.CharField(max_length=20, default='active')  # active/frozen/expired
    expire_date = models.DateField()  # 有效期
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def remaining_hours(self):
        return self.total_hours - self.used_hours - self.frozen_hours
```

#### 3.9.2 课时流水

```python
class HoursFlow(models.Model):
    account = models.ForeignKey('StudentHoursAccount', on_delete=models.CASCADE)
    schedule = models.ForeignKey('Schedule', on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=20)  # deduct/gift/freeze/refund
    hours = models.DecimalField(max_digits=10, decimal_places=1)  # 课时数量
    balance_before = models.DecimalField(max_digits=10, decimal_places=1)  # 变动前
    balance_after = models.DecimalField(max_digits=10, decimal_places=1)  # 变动后
    note = models.CharField(max_length=200, blank=True)  # 备注
    operator = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 3.9.3 扣课规则

| 场景 | 规则 |
|------|------|
| 正常上课 | 下课后扣1课时 |
| 请假 | 不扣课(提前24h) |
| 迟到 | 超过15分钟扣1课时 |
| 早退 | 不足30分钟不扣，超过扣除 |
| 旷课 | 扣1课时 |

---

### 3.10 订单管理模块

#### 3.10.1 订单

| 功能 | 描述 | 字段 |
|------|------|------|
| 创建订单 | 新增报名订单 | student/course/amount |
| 支付 | 微信/支付宝 | payment_type |
| 取消 | 超时取消 | status='cancelled' |

**数据结构**：

```python
class Order(models.Model):
    order_no = models.CharField(max_length=50, unique=True)  # 订单号
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.PROTECT)
    course_package = models.ForeignKey('CoursePackage', on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()  # 课时数
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # 订单金额
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 优惠金额
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)  # 实收金额
    payment_type = models.CharField(max_length=20)  # wechat/alipay/offline
    status = models.CharField(max_length=20, default='pending')  # pending/paid/cancelled/refunded
    expired_at = models.DateTimeField()  # 过期时间
    paid_at = models.DateTimeField(null=True)  # 支付时间
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 3.10.2 支付记录

```python
class PaymentRecord(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100)  # 第三方流水号
    status = models.CharField(max_length=20)  # success/failed
    paid_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 3.10.3 退款

```python
class RefundRecord(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, default='pending')  # pending/approved/rejected
    applicant = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    approver = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='refund_approved')
    created_at = models.DateTimeField(auto_now_add=True)
```

---

### 3.11 通知模块

#### 3.11.1 消息通知

| 功能 | 描述 | 字段 |
|------|------|------|
| 短信通知 | 验证码/通知 | 腾讯云短信 |
| 模板消息 | 微信服务号模板 | 微信公众号 |

**数据结构**：

```python
class Notification(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    type = models.CharField(max_length=20)  # sms/wechat/email
    template = models.CharField(max_length=50)  # 模板编码
    title = models.CharField(max_length=100)  # 标题
    content = models.TextField()  # 内容
    variables = models.JSONField()  # 模板变量
    status = models.CharField(max_length=20, default='pending')  # pending/sent/failed
    sent_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SmsRecord(models.Model):
    phone = models.CharField(max_length=20)
    template = models.CharField(max_length=50)
    content = models.CharField(max_length=500)
    verify_code = models.CharField(max_length=10, blank=True)  # 验证码
    status = models.CharField(max_length=20)  # success/failed
    sent_at = models.DateTimeField(auto_now_add=True)
```

---

## 4. API接口清单

### 4.1 用户权限

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/auth/register | 注册 |
| POST | /api/auth/login | 登录 |
| POST | /api/auth/logout | 登出 |
| POST | /api/auth/refresh | 刷新Token |
| POST | /api/auth/password/reset | 重置密码 |
| GET | /api/auth/me | 当前用户信息 |

### 4.2 用户管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET/POST | /api/users | 用户列表/创建 |
| GET/PUT/DELETE | /api/users/{id} | 用户详情/编辑/删除 |
| GET/POST | /api/roles | 角色列表/创建 |
| GET/PUT/DELETE | /api/roles/{id} | 角色详情/编辑/删除 |
| GET/POST | /api/menus | 菜单列表/创建 |

### 4.3 学生管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET/POST | /api/students | 学生列表/创建 |
| GET/PUT/DELETE | /api/students/{id} | 学生详情/编辑/删除 |
| POST | /api/students/import | 导入学生 |

### 4.4 教师管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET/POST | /api/teachers | 教师列表/创建 |
| GET/PUT/DELETE | /api/teachers/{id} | 教师详情/编辑/删除 |

### 4.5 课程管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET/POST | /api/courses | 课程列表/创建 |
| GET/PUT/DELETE | /api/courses/{id} | 课程详情/编辑/删除 |
| GET/POST | /api/subjects | 科目列表/创建 |
| GET/POST | /api/packages | 课程包列表/创建 |

### 4.6 班级管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET/POST | /api/classes | 班级列表/创建 |
| GET/PUT/DELETE | /api/classes/{id} | 班级详情/编辑/删除 |
| POST | /api/classes/{id}/students | 添加学生 |
| DELETE | /api/classes/{id}/students/{sid} | 移除学生 |

### 4.7 排课管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET/POST | /api/schedules | 排课列表/创建 |
| GET/PUT/DELETE | /api/schedules/{id} | 排课详情/编辑/删除 |
| GET | /api/schedules/calendar | 日历视图 |
| POST | /api/reschedules | 调课申请 |
| POST | /api/leaves | 请假申请 |

### 4.8 在线课堂

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/classrooms/create | 创建课堂 |
| GET | /api/classrooms/{schedule_id}/info | 课堂信息 |
| GET | /api/classrooms/{schedule_id}/token | 获取Token |
| POST | /api/classrooms/{schedule_id}/end | 结束课堂 |
| GET | /api/classrooms/{schedule_id}/records | 参会记录 |

### 4.9 录屏回放

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/recordings/{schedule_id} | 录制信息 |
| GET | /api/playbacks/{recording_id} | 回放信息 |
| GET | /api/playbacks/{recording_id}/url | 回放地址 |

### 4.10 课时管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/hours/accounts | 课时账户列表 |
| GET | /api/hours/accounts/{id} | 账户详情 |
| GET | /api/hours/accounts/{id}/flows | 课时流水 |

### 4.11 订单管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET/POST | /api/orders | 订单列表/创建 |
| GET | /api/orders/{id} | 订单详情 |
| POST | /api/orders/{id}/pay | 支付 |
| POST | /api/orders/{id}/cancel | 取消 |
| POST | /api/refunds | 退款申请 |

### 4.12 通知

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/notifications/sms | 发送短信 |
| POST | /api/notifications/wechat | 发送微信模板 |

---

## 5. 权限矩阵

### 5.1 功能权限

| 模块 | 超级管理员 | 教务管理员 | 教师 | 学生 | 财务 |
|------|------------|------------|------|------|------|
| 用户管理 | √ | × | × | × | × |
| 角色权限 | √ | × | × | × | × |
| 学生管理 | √ | √ | × | × | × |
| 教师管理 | √ | √ | × | × | × |
| 课程管理 | √ | √ | × | × | × |
| 班级管理 | √ | √ | × | × | × |
| 排课管理 | √ | √ | √ | × | × |
| 在线课堂 | √ | √ | √ | √ | × |
| 录屏回放 | √ | √ | √ | √ | × |
| 课时管理 | √ | √ | √ | √ | × |
| 订单管理 | √ | √ | × | × | √ |
| 退款管理 | √ | × | × | × | √ |
| 统计分析 | √ | √ | √ | √ | √ |
| 系统配置 | √ | × | × | × | × |

---

## 6. 验收标准

### 6.1 用户权限

| 用例ID | 用例描述 | 验收标准 |
|--------|----------|----------|
| U001 | 用户登录 | 输入正确账号密码，登录成功，返回JWT |
| U002 | 用户登出 | 登录状态失效 |
| U003 | Token刷新 | 获取新Token，旧Token失效 |
| U004 | 密码重置 | 短信验证码验证通过 |
| U005 | 角色分配 | 分配角色后，菜单权限正确 |
| U006 | 接口权限 | 无权限用户无法访问 |

### 6.2 学生管理

| 用例ID | 用例描述 | 验收标准 |
|--------|----------|----------|
| S001 | 创建学生 | 填写必填字段，保存成功 |
| S002 | 编辑学生 | 保存后数据正确更新 |
| S003 | 删除学生 | 状态变为deleted |
| S004 | 查询学生 | 分页/条件查询正确 |
| S005 | 导入学生 | Excel导入成功 |

### 6.3 排课管理

| 用例ID | 用例描述 | 验收标准 |
|--------|----------|----------|
| P001 | 创建排课 | 无冲突时创建成功 |
| P002 | 冲突检测 | 有冲突时提示不可排 |
| P003 | 调课 | 调课后记录正确 |
| P004 | 请假 | 请假后不扣课时 |

### 6.4 在线课堂

| 用例ID | 用例描述 | 验收标准 |
|--------|----------|----------|
| C001 | 创建课堂 | 腾讯会议创建成功 |
| C002 | 进入课堂 | 获取Token，加入会议 |
| C003 | 结束课堂 | 会议结束，状态更新 |
| C004 | 自动录制 | 课次开始时自动录制 |

### 6.5 课时管理

| 用例ID | 用例描述 | 验收���准 |
|--------|----------|----------|
| H001 | 购买课程 | 账户创建，课时正确 |
| H002 | 正常上课 | 下课后扣1课时 |
| H003 | 查询余额 | 显示剩余课时正确 |

### 6.6 订单管理

| 用例ID | 用例描述 | 验收标准 |
|--------|----------|----------|
| O001 | 创建订单 | 订单创建成功，待支付 |
| O002 | 支付成功 | 订单状态变为paid |
| O003 | 退款 | 退款通过，课时回退 |

---

## 7. 技术依赖

### 7.1 Python包

```txt
Django>=4.2
djangorestframework>=3.14
django-cors-headers>=4.0
psycopg2-binary>=2.9
redis>=4.5
celery>=5.3
PyJWT>=2.8
tencentcloud-sdk-python-core>=3.0
wemeet-openapi-sdk-python>=1.0
python-dotenv>=1.0
Pillow>=10.0
openpyxl>=3.1
```

### 7.2 前端包

```json
{
  "vue": "^3.3",
  "element-plus": "^2.4",
  "@element-plus/icons-vue": "^2.3",
  "axios": "^1.5",
  "pinia": "^2.1",
  "vue-router": "^4.2",
  "dayjs": "^1.11",
  "echarts": "^5.4",
  "@tinymce/tinymce-vue": "^5.1"
}
```

---

## 8. 附录

### 8.1 数据库ER图

见 `05_数据库设计/01_ER图/`

### 8.2 业务流程图

见 `02_产品设计调研/03_业务流程图/`

### 8.3 字段字典

见 `02_产品设计调研/04_字段字典/`

---

**文档结束**