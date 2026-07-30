---
name: project-work
description: "优惠券中心项目工作技能：定义项目资源地图、代码/配置/文档的位置关系，以及修改代码时必须同步更新的文档规则。用于确保每次功能开发、UI修改、配置变更都能正确维护项目文档的一致性。"
---

# 项目工作技能 - 优惠券发放与核销中心

本技能定义了项目的完整资源地图和变更联动规则。每次开发、修改时必须遵守这些规则，保证文档与代码的一致性。

---

## 一、项目资源地图

### 1.1 项目根目录结构

```
aws20260729/                         # 项目根目录
├── .aidlc/                          # AIDLC 开发生命周期文档
│   ├── plan/                        # 阶段计划文件
│   ├── requirements/                # 需求文档
│   ├── design/                      # 设计文档
│   └── tasks.md                     # 实现任务清单
├── .kiro/                           # Kiro 配置
│   └── skills/                      # 技能定义
├── coupon-center/                   # 主应用代码（Flask）
├── skill/                           # 外部技能集合
├── goal/                            # 目标文档
├── requirement/                     # 外部需求参考
├── history.md                       # 项目交互历史与变更记录
├── setup.md                         # 项目完整说明文档
├── job.md                           # 工作任务
├── bedrock.service.ts               # Bedrock 参考实现（TypeScript）
└── CLAUDE.md                        # AI 助手指令
```

### 1.2 应用代码目录（coupon-center/）

```
coupon-center/
├── app.py                           # Flask 应用入口
├── config.py                        # 应用配置（读取 .env）
├── extensions.py                    # Flask 扩展实例（db, migrate, login_manager, csrf）
├── seed.py                          # 种子数据脚本
├── requirements.txt                 # Python 依赖清单
├── .env                             # 环境变量（密钥、AWS凭证、模型ID）
├── .env.example                     # 环境变量模板
├── models/                          # 数据模型（SQLAlchemy ORM）
│   ├── user.py                      # 用户模型
│   ├── campaign.py                  # 活动模型
│   ├── coupon.py                    # 优惠券实例模型
│   ├── redemption.py                # 核销记录模型
│   ├── notification.py              # 通知模型
│   ├── operation_log.py             # 操作日志模型
│   ├── risk_log.py                  # 风控日志模型
│   ├── share_link.py                # 分享链接模型
│   ├── blacklist.py                 # 黑白名单模型
│   ├── template.py                  # 活动模板模型
│   └── favorite.py                  # 收藏模型
├── services/                        # 业务服务层
│   ├── bedrock_service.py           # AWS Bedrock AI 调用封装
│   ├── ai_copy_service.py           # AI 文案生成服务
│   ├── ai_profile_service.py        # AI 用户画像服务
│   ├── ai_recommend_service.py      # AI 智能推荐服务
│   ├── auth_service.py              # 认证服务
│   ├── campaign_service.py          # 活动管理服务
│   ├── coupon_service.py            # 优惠券服务
│   ├── redemption_service.py        # 核销服务
│   ├── risk_engine.py               # 风控引擎
│   ├── notification_service.py      # 通知服务
│   ├── share_service.py             # 分享服务
│   ├── log_service.py               # 日志服务
│   └── stats_service.py             # 统计服务
├── routes/                          # 路由/控制器层
│   ├── auth.py                      # 认证路由（登录/注册）
│   ├── user.py                      # 用户页面路由
│   ├── operator.py                  # 运营页面路由
│   ├── verifier.py                  # 核销页面路由
│   ├── admin.py                     # 管理员页面路由
│   ├── api.py                       # API 接口路由
│   └── share.py                     # 分享页面路由
├── templates/                       # Jinja2 HTML 模板
│   ├── base.html                    # 全局布局（侧边栏+顶栏）
│   ├── share.html                   # 分享领券页面
│   ├── auth/                        # 认证页面（login/register）
│   ├── user/                        # 用户端页面
│   ├── operator/                    # 运营端页面
│   ├── verifier/                    # 核销端页面
│   ├── admin/                       # 管理员页面
│   └── example/                     # UI 参考设计样例
├── docs/                            # 项目文档
│   └── ui-element-ids.md            # UI 元素 ID 接口说明（自动化测试用）
└── instance/
    └── coupon_center.db             # SQLite 数据库文件
```

---

## 二、关键文档及用途

| 文档路径 | 用途 | 维护时机 |
|----------|------|----------|
| `history.md` | 项目交互历史、功能变更、技术决策记录 | 每次增加功能、修复Bug、做出技术决策时 |
| `coupon-center/docs/ui-element-ids.md` | UI 元素 ID 接口说明，自动化测试用 | 修改/新增/删除 HTML 模板中的 id 属性时 |
| `setup.md` | 项目完整说明（需求、架构、API、页面） | 需求或架构层面变更时 |
| `.aidlc/tasks.md` | 实现任务清单及完成状态 | 任务完成时勾选，新增需求时追加任务 |
| `coupon-center/requirements.txt` | Python 依赖 | 新增/删除/升级第三方库时 |
| `coupon-center/.env.example` | 环境变量模板 | 新增环境变量时 |

---

## 三、变更联动规则（必须遵守）

### 规则 1：修改 UI 控件 → 更新 ui-element-ids.md

**触发条件：** 修改了 `coupon-center/templates/` 下任何 HTML 文件中带有 `id` 属性的元素

**必须执行：**
- 如果是**新增**带 id 的元素：在 `coupon-center/docs/ui-element-ids.md` 对应页面章节新增一行
- 如果是**删除**带 id 的元素：从 `ui-element-ids.md` 中移除对应行
- 如果是**修改** id 值（不推荐）：同步更新 `ui-element-ids.md` 中的 ID 列
- **不得改动已有元素的 id 属性**（除非有充分理由并全局搜索影响）

**ID 命名规则：** `<页面功能>_<组件功能>_<组件类型>_<随机4位>`

**涉及文件关系：**
```
templates/auth/login.html       ←→  ui-element-ids.md § 1. 登录页面
templates/auth/register.html    ←→  ui-element-ids.md § 2. 注册页面
templates/verifier/index.html   ←→  ui-element-ids.md § 3. 核销页面
templates/operator/create.html  ←→  ui-element-ids.md § 4. 创建活动页面
templates/user/*                ←→  ui-element-ids.md § 5. 动态渲染组件
templates/base.html             ←→  ui-element-ids.md § 6. 侧边栏导航
```

---

### 规则 2：增加功能 → 更新 history.md

**触发条件：** 完成了一个新功能开发、Bug修复、技术变更、UI重构

**必须执行：**
- 在 `history.md` 末尾追加一个新的日期段落（如果当日已有则在当日段落下追加）
- 记录格式：
  ```markdown
  ## YYYY-MM-DD <变更主题>

  ### 变更内容
  - 具体做了什么
  - 受影响的文件列表

  ### 技术决策（如有）
  - 为什么这么做
  ```

---

### 规则 3：修改 API 接口 → 更新相关文档

**触发条件：** 修改了 `coupon-center/routes/api.py` 中的接口

**必须执行：**
- 更新 `coupon-center/docs/ui-element-ids.md` § 7. API 接口 中的对应行
- 如果是全新接口，追加到表格中
- 如果修改了请求/响应格式，更新请求体列

---

### 规则 4：新增数据模型字段 → 更新 seed.py

**触发条件：** 修改了 `coupon-center/models/` 下的模型文件，新增了字段

**必须执行：**
- 检查 `coupon-center/seed.py` 是否需要适配新字段
- 如果新字段是 NOT NULL 且无默认值，必须更新 seed 数据
- 删除旧的 `instance/coupon_center.db` 并重新运行 seed

---

### 规则 5：新增路由/页面 → 更新导航和路由文档

**触发条件：** 新增了页面路由

**必须执行：**
- 在 `templates/base.html` 侧边栏中添加对应导航链接
- 更新 `ui-element-ids.md` § 6. 侧边栏导航链接 表格
- 如果有新增页面中的可交互元素带 id，在 `ui-element-ids.md` 对应章节登记

---

### 规则 6：修改环境变量 → 更新 .env.example

**触发条件：** 在代码中读取了新的环境变量（`os.getenv('NEW_VAR')`）

**必须执行：**
- 在 `coupon-center/.env.example` 中添加该变量及注释说明
- 如果是关键配置变更，在 `history.md` 中记录

---

### 规则 7：修改依赖 → 更新 requirements.txt

**触发条件：** 代码中 import 了新的第三方库

**必须执行：**
- 将新依赖添加到 `coupon-center/requirements.txt`
- 使用固定版本号（如 `flask==3.0.0`）

---

## 四、配置文件位置索引

| 配置类型 | 文件路径 | 说明 |
|----------|----------|------|
| Flask 应用配置 | `coupon-center/config.py` | 数据库URI、JWT密钥、AWS配置 |
| 环境变量 | `coupon-center/.env` | 实际运行时的密钥和凭证 |
| 环境变量模板 | `coupon-center/.env.example` | 团队共享的配置模板 |
| Python 依赖 | `coupon-center/requirements.txt` | pip install -r requirements.txt |
| Git 忽略 | `.gitignore` | 排除 .env, __pycache__, instance/ 等 |
| AIDLC 任务 | `.aidlc/tasks.md` | 开发任务跟踪 |

---

## 五、代码层级与调用关系

```
请求流入方向：

[浏览器] → routes/ (路由层)
              ├── auth.py      → services/auth_service.py
              ├── api.py       → services/* (各业务服务)
              ├── user.py      → templates/user/*
              ├── operator.py  → templates/operator/*
              ├── verifier.py  → templates/verifier/*
              ├── admin.py     → templates/admin/*
              └── share.py     → templates/share.html

服务层调用：
services/
├── bedrock_service.py          ← ai_copy_service / ai_recommend_service / ai_profile_service / risk_engine
├── coupon_service.py           ← risk_engine (领券时风控检查)
├── notification_service.py     ← coupon_service / share_service (操作后发通知)
└── log_service.py              ← 所有关键操作 (记录操作日志)

数据层：
models/* → extensions.py (db 实例) → instance/coupon_center.db (SQLite)
```

---

## 六、常用开发操作速查

| 操作 | 命令 | 工作目录 |
|------|------|----------|
| 启动应用 | `python app.py` | `coupon-center/` |
| 初始化种子数据 | `python seed.py` | `coupon-center/` |
| 安装依赖 | `pip install -r requirements.txt` | `coupon-center/` |
| 重置数据库 | 删除 `instance/coupon_center.db` 后重新 `python seed.py` | `coupon-center/` |
| 访问地址 | http://localhost:5000 | - |

### 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 运营人员 | operator | oper123 |
| 核销人员 | verifier | verify123 |
| 普通用户 | user1 | user123 |

---

## 七、变更检查清单

每次完成代码修改后，按此清单逐项检查：

- [ ] 是否修改了 HTML 模板中的 id 属性？→ 更新 `ui-element-ids.md`
- [ ] 是否增加/修改了功能？→ 更新 `history.md`
- [ ] 是否修改了 API 接口？→ 更新 `ui-element-ids.md` § 7
- [ ] 是否新增了数据模型字段？→ 检查 `seed.py`
- [ ] 是否新增了页面/路由？→ 更新 `base.html` 导航 + `ui-element-ids.md` § 6
- [ ] 是否使用了新环境变量？→ 更新 `.env.example`
- [ ] 是否引入了新依赖？→ 更新 `requirements.txt`
- [ ] 是否涉及架构/需求变更？→ 更新 `setup.md`
