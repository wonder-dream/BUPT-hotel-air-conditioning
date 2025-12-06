# 波普特廉价酒店中央空调计费系统

## 📋 项目概述

本项目是北京邮电大学软件工程课程作业，实现了一个酒店中央空调计费管理系统。系统模拟了酒店空调的调度、控制、计费等功能，支持多房间并发服务、优先级调度和时间片调度算法。

### 项目背景

波普特廉价酒店需要一套中央空调计费系统，要求：
- 支持制冷/制热两种模式
- 实现多房间空调调度（最多同时服务 y=3 个房间）
- 按风速优先级调度（高风 > 中风 > 低风）
- 支持时间片轮转调度（时间片 s=120 秒）
- 按能耗计费（1 元/度）

---

## 🏗️ 系统架构

```
BUPT-air-conditioning/
├── backend/                    # Django 后端
│   ├── ac_system/             # 空调系统核心应用
│   │   ├── models.py          # 数据模型定义
│   │   ├── views.py           # API 视图
│   │   ├── services.py        # 业务逻辑层
│   │   ├── scheduler.py       # 空调调度器（核心）
│   │   ├── serializers.py     # 序列化器
│   │   ├── urls.py            # URL 路由
│   │   └── apps.py            # 应用配置（调度器启动）
│   ├── hotel_ac/              # Django 项目配置
│   ├── config.py              # 系统参数配置
│   ├── init_data.py           # 初始化数据脚本
│   ├── manage.py              # Django 管理脚本
│   └── requirements.txt       # Python 依赖
│
├── frontend/                   # Vue.js 前端
│   ├── src/
│   │   ├── views/             # 页面组件
│   │   │   ├── CustomerPanel.vue    # 客户空调控制面板
│   │   │   ├── Reception.vue        # 前台（入住/结账/房态）
│   │   │   ├── Monitor.vue          # 管理员监控面板
│   │   │   └── Report.vue           # 统计报表
│   │   ├── api/               # API 接口封装
│   │   ├── router/            # 路由配置
│   │   ├── App.vue            # 根组件
│   │   └── main.js            # 入口文件
│   ├── package.json           # 前端依赖
│   └── vite.config.js         # Vite 配置
│
├── document/                   # 需求文档
├── start_backend.bat          # 后端启动脚本
├── start_frontend.bat         # 前端启动脚本
└── TEST_GUIDE.md              # 测试指南
```

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus |
| 后端 | Django 4.2 + Django REST Framework |
| 数据库 | SQLite |
| 通信 | RESTful API |

---

## 📊 核心功能模块

### 1. 用户角色与功能

| 角色 | 功能 | 对应页面 |
|------|------|----------|
| 顾客 | 空调开关、调温、调风速、查看费用 | `/room/{房间号}` (如 `/room/301`) |
| 前台 | 办理入住、结账、查看房态 | `/reception` |
| 管理员 | 监控所有空调状态、批量控制 | `/monitor` |
| 经理 | 查看统计报表 | `/report` |

### 2. 空调调度算法

系统实现了**优先级调度 + 时间片调度**的混合调度算法：

#### 优先级调度
- **高风（high）**: 优先级 3
- **中风（medium）**: 优先级 2
- **低风（low）**: 优先级 1

当服务队列已满时，高优先级请求可以抢占低优先级服务。

#### 时间片调度
- 时间片大小：**120 秒**
- 当等待队列中的请求等待满一个时间片后，可以与同优先级（或更低优先级）的服务对象交换
- **等待期间停止送风和计费**，不消耗能量

#### 调度流程
```
新请求到达
    ↓
服务队列满？ ──否──→ 直接分配服务
    ↓是
检查优先级抢占 ──可抢占──→ 抢占低优先级服务
    ↓不可抢占
加入等待队列
    ↓
等待时间片到期 → 与服务队列轮换
```

### 3. 温度控制逻辑

| 模式 | 温度范围 | 行为 |
|------|----------|------|
| 制冷 | 18°C - 25°C | 降温 |
| 制热 | 25°C - 30°C | 升温 |

- **缺省温度**: 25°C
- **初始室温**: 28°C（模拟环境温度）
- **温度偏离阈值**: 1°C（超过此值自动重启）

#### 温度变化率（度/分钟）
| 风速 | 制温速率 | 能耗速率 |
|------|----------|----------|
| 高风 | 0.6 | 1.0 |
| 中风 | 0.5 | 0.5 |
| 低风 | 0.4 | 0.33 |

#### 待机与重启机制
- 达到目标温度后进入**待机状态**（释放服务槽位）
- 温度偏离目标温度超过 1°C 时**自动重启**

### 4. 计费系统

| 项目 | 计算方式 |
|------|----------|
| 空调费 | 1 元/度（按实际能耗计算） |
| 房费 | 按房型计价（标准间 400、豪华间 600、套房 800 元/天） |

---

## 🗃️ 数据库模型

### ER 关系图

```
Room(房间)
  ├── room_id (PK)          # 房间号，如 "301"
  ├── room_type             # 房型：standard/deluxe/suite
  ├── status                # 状态：available/occupied/maintenance
  └── price_per_day         # 每日房价

Customer(顾客)
  ├── customer_id (PK)      # 顾客ID
  ├── name                  # 姓名
  ├── id_card               # 身份证号
  └── phone                 # 手机号

AccommodationOrder(入住订单)
  ├── order_id (PK)         # 订单ID
  ├── customer_id (FK)      # 关联顾客
  ├── room_id (FK)          # 关联房间
  ├── check_in_time         # 入住时间
  ├── check_out_time        # 退房时间
  ├── status                # 状态：active/completed/cancelled
  └── room_fee              # 房费

ACState(空调状态)
  ├── room_id (PK, FK)      # 房间号（与房间一对一）
  ├── is_on                 # 是否开机
  ├── status                # 状态：on/off/standby/waiting
  ├── mode                  # 模式：cooling/heating
  ├── current_temp          # 当前温度
  ├── target_temp           # 目标温度
  ├── fan_speed             # 风速：low/medium/high
  ├── total_cost            # 累计费用
  └── total_energy          # 累计耗电量

ACDetailRecord(空调详单)
  ├── record_id (PK)        # 详单ID
  ├── room_id (FK)          # 关联房间
  ├── order_id (FK)         # 关联订单
  ├── start_time            # 开始时间
  ├── end_time              # 结束时间
  ├── start_temp            # 开始温度
  ├── end_temp              # 结束温度
  ├── target_temp           # 目标温度
  ├── fan_speed             # 风速
  ├── mode                  # 模式
  ├── energy_consumed       # 耗电量
  └── cost                  # 费用

AccommodationBill(住宿账单)
  ├── bill_id (PK)          # 账单ID
  ├── order_id (FK)         # 关联订单
  ├── room_fee              # 房费
  ├── ac_fee                # 空调费
  ├── total_fee             # 总费用
  └── is_paid               # 是否已支付
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 或 yarn

### 安装步骤

#### 1. 克隆项目
```bash
git clone <repository-url>
cd BUPT-air-conditioning
```

#### 2. 后端安装
```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 初始化数据（创建房间）
python init_data.py

# 启动后端服务器
python manage.py runserver
```

#### 3. 前端安装
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 4. 快速启动（Windows）
也可以直接使用启动脚本：
- `start_backend.bat` - 启动后端服务
- `start_frontend.bat` - 启动前端服务

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:5173 |
| 后端 API | http://localhost:8000/api/ |
| Django Admin | http://localhost:8000/admin/ |

---

## 📖 API 文档

### 房间管理

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/rooms/` | 获取所有房间（含入住信息） |
| GET | `/api/rooms/available/` | 获取可用房间列表 |

### 入住/结账

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/checkin/` | 办理入住 |
| POST | `/api/checkout/` | 办理退房 |
| GET | `/api/bill/{room_id}/` | 获取账单详情 |
| POST | `/api/pay/` | 支付账单 |

#### 入住请求示例
```json
{
  "name": "张三",
  "phone": "13800138000",
  "id_card": "110101199001011234",
  "room_id": "301"
}
```

### 空调控制

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/ac/control/` | 空调控制（开关/调温/调风） |
| GET | `/api/ac/state/{room_id}/` | 获取空调状态 |
| GET | `/api/ac/monitor/` | 获取所有空调状态（监控用） |

#### 空调控制请求示例
```json
// 开机
{
  "room_id": "301",
  "action": "power_on",
  "target_temp": 22,
  "fan_speed": "medium",
  "mode": "cooling"
}

// 关机
{
  "room_id": "301",
  "action": "power_off"
}

// 调温（不触发调度）
{
  "room_id": "301",
  "action": "change_temp",
  "target_temp": 24,
  "mode": "cooling"
}

// 调风速（触发调度）
{
  "room_id": "301",
  "action": "change_speed",
  "fan_speed": "high"
}
```

### 报表

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/orders/` | 获取订单列表 |
| GET | `/api/report/?type=daily&date=2025-01-01` | 获取日报表 |

---

## 🖥️ 页面功能说明

### 1. 客户空调面板 (`/room/{房间号}`)

每个房间有独立的控制页面，不能切换到其他房间：
- `/room/301` - 301房间
- `/room/302` - 302房间
- `/room/303` - 303房间
- `/room/304` - 304房间
- `/room/305` - 305房间

**功能特性**：
- 空调开关控制
- 制冷/制热模式切换
- 温度调节（滑块 + 按钮）
- 风速选择（低/中/高）
- 实时显示当前温度、费用
- 状态提示（等待中/待机中）

### 2. 前台服务 (`/reception`)

**功能模块**：

#### 入住办理
- 填写客户信息（姓名、手机、身份证）
- 选择可用房间
- 确认入住后显示订单信息

#### 结账办理
- 输入房间号查询账单
- 显示房费、空调费、总费用
- 一键支付退房

#### 房间状态
- 查看所有房间入住情况
- 显示入住客人信息（姓名、手机、入住时间）
- 身份证号脱敏显示

### 3. 管理员监控 (`/monitor`)

**功能特性**：
- 实时显示所有房间空调状态
- 统计概览（运行中/等待中/待机/关闭）
- 服务队列和等待队列可视化
- 批量设置温度、风速
- 2 秒自动刷新

### 4. 统计报表 (`/report`)

**功能特性**：
- 按日期查询统计数据
- 总收入、房费收入、空调收入统计
- 入住人数统计
- 订单记录列表

---

## ⚙️ 配置说明

系统参数在 `backend/config.py` 中配置：

```python
# 房间配置
TOTAL_ROOMS = 5            # 酒店总房间数
MAX_SERVICE_NUM = 3        # 同时服务上限
WAIT_TIME_SLICE = 120      # 等待时间片（秒）

# 温度配置
DEFAULT_TEMP = 25          # 缺省温度
COOLING_MIN_TEMP = 18      # 制冷最低温度
COOLING_MAX_TEMP = 25      # 制冷最高温度
HEATING_MIN_TEMP = 25      # 制热最低温度
HEATING_MAX_TEMP = 30      # 制热最高温度
TEMP_THRESHOLD = 1         # 温度偏离阈值

# 风速配置（度/分钟）
FAN_SPEED_POWER = {
    "low": 1/3,            # 低风：0.33度/分钟
    "medium": 0.5,         # 中风：0.5度/分钟
    "high": 1.0            # 高风：1度/分钟
}

# 计费标准
PRICE_PER_DEGREE = 1       # 1元/度

# 房间价格（元/天）
ROOM_PRICE = {
    "standard": 400,       # 标准间
    "deluxe": 600,         # 豪华间
    "suite": 800           # 套房
}
```

---

## 🔧 调度器核心实现

调度器位于 `backend/ac_system/scheduler.py`，采用**调度对象与服务对象分离**的架构设计：

### 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                  ACScheduler（调度对象）                      │
│                                                             │
│  职责：                                                      │
│  - 管理服务队列和等待队列                                     │
│  - 优先级调度（抢占调度）                                     │
│  - 时间片调度（轮转调度）                                     │
│  - 请求防抖处理                                              │
│                                                             │
│               ↓ 委托实际操作                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               ACServiceManager（服务对象）                    │
│                                                             │
│  职责：                                                      │
│  - 更新房间温度（制冷/制热）                                  │
│  - 计算能耗和费用                                            │
│  - 管理详单记录（创建、更新、结束）                            │
│  - 管理房间状态                                              │
└─────────────────────────────────────────────────────────────┘
```

### 类结构

```python
class ServiceObject:      # 正在服务的房间数据对象
class WaitingObject:      # 等待队列中的房间数据对象
class ACServiceManager:   # 服务对象 - 负责温控、计费、详单
class ACScheduler:        # 调度对象 - 负责调度决策（单例）
```

### 职责分离

| 功能 | 调度对象 (ACScheduler) | 服务对象 (ACServiceManager) |
|------|------------------------|----------------------------|
| 队列管理 | ✅ | - |
| 优先级调度 | ✅ | - |
| 时间片调度 | ✅ | - |
| 温度计算 | - | ✅ |
| 费用计算 | - | ✅ |
| 详单记录 | - | ✅ |
| 房间状态 | - | ✅ |

### 调度器主循环

```python
def _scheduler_loop(self):
    while self.running:
        self._process_pending_requests()  # 处理待处理请求（防抖）
        self._update_all_temperatures()   # 委托 ServiceManager 更新温度
        self._check_wait_queue()          # 检查等待队列（时间片调度）
        self._check_target_reached()      # 检查是否达到目标温度
        time.sleep(1)                     # 每秒执行一次
```

### 关键方法

| 类 | 方法 | 功能 |
|------|------|------|
| ACScheduler | `submit_request()` | 提交空调控制请求（带防抖） |
| ACScheduler | `_power_on()` | 处理开机请求 |
| ACScheduler | `_schedule_request()` | 调度新请求（优先级/时间片） |
| ACScheduler | `_move_to_wait_queue()` | 将服务对象移至等待队列 |
| ACScheduler | `_allocate_from_wait_queue()` | 从等待队列分配服务 |
| ACScheduler | `_check_target_reached()` | 检查是否达到目标温度，进入待机 |
| ACServiceManager | `update_service_temperature()` | 更新房间温度和费用 |
| ACServiceManager | `create_detail_record()` | 创建空调使用详单 |
| ACServiceManager | `end_detail_record()` | 结束空调使用详单 |
| ACServiceManager | `check_target_reached()` | 检查是否达到目标温度 |

---

## ⚠️ 未完成功能与待优化项

### 🔴 未完成功能

1. **用户认证系统**
   - 当前无登录功能，各角色页面直接可访问
   - 需实现：用户注册、登录、JWT Token 认证、权限控制

2. **周报表/月报表**
   - 目前只实现了日报表
   - 需扩展 `ReportService` 支持周/月统计

3. **空调详单查询**
   - 数据库已记录详单 (`ACDetailRecord`)
   - 前端缺少详单查询和展示页面

4. **打印功能**
   - 需求文档要求支持打印账单、报表
   - 目前未实现

5. **管理员设置功能**
   - 空调工作模式切换（只制冷/只制热）
   - 运行参数在线配置

### 🟡 待优化项

1. **数据持久化**
   - 调度器状态保存在内存中，服务器重启后丢失
   - 建议：定期同步到数据库或使用 Redis 缓存

2. **费用统计精度**
   - 从详单汇总费用 vs 调度器实时计费可能存在误差
   - 建议：统一使用详单汇总作为最终费用

3. **并发处理**
   - 高并发场景下可能存在竞态条件
   - 建议：增加数据库事务锁、使用线程锁

4. **前端状态管理**
   - 当前使用 `ref` 管理状态，页面间数据不共享
   - 建议：引入 Pinia 状态管理库

5. **错误处理**
   - API 错误提示不够友好
   - 建议：统一错误处理中间件和用户提示

6. **测试覆盖**
   - 缺少自动化测试
   - 建议：添加 pytest 单元测试和集成测试

7. **UI/UX 改进**
   - 移动端适配不完善
   - 缺少加载状态和骨架屏
   - 缺少操作确认弹窗

### 🟢 建议新增功能

1. **WebSocket 实时通信**
   - 替代前端轮询，提高实时性和性能
   
2. **空调预约功能**
   - 支持定时开关机

3. **能耗分析图表**
   - 使用 ECharts 展示能耗趋势、房间使用率

4. **多语言支持**
   - 国际化 (i18n) 支持

5. **日志系统**
   - 记录操作日志，方便审计

---

## 🐛 已知问题

1. **调度器重启问题**
   - Django 开发服务器会启动两次（auto-reloader），导致调度器重复启动
   - 当前解决方案：在 `apps.py` 中检查 `RUN_MAIN` 环境变量

2. **时区问题**
   - 前端显示时间可能与服务器时间不一致
   - 建议：统一使用 UTC 或在 Django settings 中配置正确时区

3. **房间温度不同步**
   - 页面切换后需要重新获取状态
   - 依赖前端轮询机制

---

## 📝 测试说明

参见 [TEST_GUIDE.md](./TEST_GUIDE.md) 获取详细测试流程。

### 基本测试流程

1. 启动后端和前端服务
2. 访问前台页面 `/reception` 办理入住
3. 访问客户面板 `/room/301`、`/room/302` 等测试空调控制
4. 同时开启多个房间空调测试调度
5. 访问监控页面 `/monitor` 查看调度队列
6. 办理退房验证计费

### 调度测试场景

1. **优先级抢占测试**：
   - 先开启 3 个低风房间（队列满）
   - 再开启 1 个高风房间
   - 预期：高风抢占 1 个低风，低风进入等待队列

2. **时间片调度测试**：
   - 开启 4 个中风房间
   - 等待 120 秒
   - 预期：等待队列与服务队列轮换（等待期间停止送风计费）

3. **待机重启测试**：
   - 开启空调，设置目标温度
   - 等待温度达到目标值
   - 预期：进入待机状态
   - 继续等待温度偏离 1°C
   - 预期：自动重启

---

## 👥 团队信息

- **课程**：软件工程
- **学校**：北京邮电大学
- **班级_小组**：2023219108_108e
- **学期**：2025 春季

---

## 📄 许可证

本项目仅用于学习交流，不得用于商业目的。

---

## 🔗 参考资料

- [Django 官方文档](https://docs.djangoproject.com/)
- [Vue 3 官方文档](https://cn.vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Vite](https://cn.vitejs.dev/)

---

© 2025 波普特酒店空调管理系统
