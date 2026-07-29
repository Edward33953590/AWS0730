# 优惠券发放与核销中心 - 项目说明文档

## 一、项目概述

构建一个**优惠券发放与核销系统**，运营人员创建优惠券活动，普通用户领取和使用优惠券，核销人员负责核销管理，管理员查看统计数据和监控异常。系统引入 Amazon Bedrock AI 能力提升用户体验与安全性。

项目采用**单机本地部署**方式，通过 API Token 调用 Amazon Bedrock 模型提供 AI 推理能力。演示时通过注册/登录不同角色账户模拟各类用户的操作流程。

---

## 二、技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 前端 | Next.js + React + TailwindCSS | 美观实用，简洁大方的UI风格 |
| 后端 | Next.js API Routes | 全栈框架，前后端一体 |
| 数据库 | SQLite (Prisma ORM) | 单机部署友好，无需额外数据库服务 |
| AI服务 | Amazon Bedrock Converse API | 参考 bedrock.service.ts，支持 SDK 凭证 / API Key 双模式 |
| 认证 | 自研用户名+密码 (bcrypt) + JWT | 注册时选择角色 |
| 部署 | 本地运行 (localhost) | 开发即演示环境 |

---

## 三、用户角色与权限

| 角色 | 权限范围 |
|------|----------|
| 管理员 | 查看统计面板、监控异常、数据导出、查看操作日志、系统配置 |
| 运营人员 | 创建/编辑/管理优惠券活动、设置活动参数、审核风控标记、批量发券、黑白名单管理、活动模板 |
| 核销人员 | 优惠券核销操作、核销记录查询 |
| 普通用户 | 注册登录、浏览优惠券、领取优惠券、使用优惠券、转赠、收藏、查看个人券包 |

注册方式：用户名 + 密码，注册界面提供角色选择下拉菜单。

---

## 四、优惠券类型（7种）

> **说明：** 运营人员创建活动时，优惠券的金额和类型均可自由选择和设置，但每种类型都有合理的默认值，方便快速创建活动。

| 类型 | 说明 | 核心参数 | 默认值 |
|------|------|----------|--------|
| 满减券 | 消费满X减Y | 满足金额、减免金额 | 满100减20 |
| 折扣券 | 按比例打折 | 折扣比例（如0.8=8折） | 8折 |
| 无门槛券 | 无消费门槛直接减免 | 减免金额 | 减5元 |
| 加购券 | 购买指定商品可低价加购另一商品 | 主商品、加购商品、加购价格 | 加1元换购 |
| 品类券 | 限定品类使用 | 适用品类、满足金额、减免金额 | 满50减10 |
| 新人券 | 新注册用户专享 | 减免金额/折扣、仅新用户可领 | 减15元 |
| 限时券 | 限定时间段可用 | 可用开始时间、可用结束时间 | 当天11:00-13:00 |

**运营人员创建活动时的表单行为：**
- 选择优惠券类型后，自动填充该类型的默认金额/参数
- 运营人员可修改任意参数值
- 库存默认100张、有效期默认1天、每人限领默认1张（均可修改）

---

## 五、核心功能模块

### 5.1 活动管理（运营人员）

- 创建/编辑优惠券活动
- 活动参数：名称、类型、面额/折扣、库存数量、有效期（默认1天，可自定义）、每用户限领数
- 设置是否可转赠（开关）
- 设置是否可叠加使用（开关）
- 设置分享领取次数（默认3次）
- 活动定时开始（设置开放领取时间）
- AI智能文案生成（自动生成活动标题、描述、营销话术）
- 活动模板（保存/加载常用配置）
- 批量发券（选择用户批量发放）
- 黑白名单管理

### 5.2 用户领券

- 浏览可用优惠券列表
- 领取优惠券
  - 库存原子扣减（不可超发）
  - 每用户限领校验
  - 新人券仅新用户可领
  - 限时券时间校验
- 优惠券收藏夹
- 领券进度条（剩余库存百分比展示）
- 优惠券排行榜（最受欢迎TOP榜）
- 分享领券（生成分享链接，限次数）
- 优惠券转赠（转赠给其他用户）

### 5.3 核销管理（核销人员）

- **核销方式**：核销人员输入优惠券唯一券码，点击"核销"按钮完成核销
- 核销人员UI上有输入券码的输入框 + 核销按钮，操作简洁直接
- 幂等核销（重复请求返回一致结果）
- 过期券不可核销
- 已核销券不可再次核销
- 核销记录查询

### 5.4 统计面板（管理员）

- 领取率、核销率、剩余库存
- 数据可视化图表（图形化展示）
- 数据导出（CSV/Excel）
- 各类型优惠券使用分析

### 5.5 操作日志

- 记录所有关键操作：领券、核销、风控拦截、活动创建/修改、转赠等
- 按时间、操作类型、用户筛选
- 管理员可查看全部日志

### 5.6 通知消息

- **纯站内通知**（页面内消息列表，铃铛图标 + 未读数）
- 领券成功通知
- 优惠券即将过期提醒
- 转赠通知（收到转赠的券）
- 风控拦截通知

---

## 六、AI 增强功能

### 6.1 智能推券

- 根据用户历史行为（领券记录、核销记录、浏览行为）
- 调用 Bedrock AI 生成个性化推荐列表 + 推荐理由文本
- 返回非空推荐列表

### 6.2 异常检测（风控）

- 领券时评估用户行为风险
- 返回风险评分与决策：放行 / 拦截 / 人工审核
- AI 不可用时降级为规则引擎（如：10秒内50次领取 → 拦截）
- **AI异常行为解释**：用自然语言解释为什么判定为异常

### 6.3 AI智能文案生成

- 运营创建活动时，一键生成：
  - 活动标题
  - 优惠券描述
  - 营销话术/推广文案

### 6.4 AI用户画像分析

- 根据用户领券/核销行为数据
- AI 生成用户画像标签（如：价格敏感型、高频用户、品类偏好等）

---

## 七、功能边界与验收标准

| 编号 | 验收场景 | 预期结果 |
|------|----------|----------|
| AC-1 | 库存为N，N+1个并发领取请求 | 只有N个成功 |
| AC-2 | 同一用户重复领取 | 第二次返回"已领取" |
| AC-3 | 过期券核销 | 返回"券已过期" |
| AC-4 | 重复核销 | 幂等，多次结果相同 |
| AC-5 | AI推荐 | 返回非空推荐列表+理由文本 |
| AC-6 | 短时间高频领取（10秒50次） | 触发风控拦截 |
| AC-7 | 用户注册登录 | 成功注册、登录、角色权限生效 |
| AC-8 | 优惠券转赠 | 转赠后原用户券消失，目标用户获得券 |
| AC-9 | 分享领券超过次数限制 | 超出设定次数后领取失败 |
| AC-10 | AI文案生成 | 创建活动时生成有效的文案内容 |

**不包含的功能：** 金额结算、支付对接。

---

## 八、竞赛演示流程（参考）

1. 创建库存为 1 的活动（展示AI文案生成）
2. 用户 A 领取 → 成功（展示AI推荐理由 + 领券进度条变化）
3. 用户 B 领取同一券 → 失败（库存不足）
4. 用户 A 核销 → 成功
5. 用户 A 再次核销 → 返回"已核销"
6. 用户 C 10秒内50次领取 → 风控拦截（展示AI异常解释）
7. 展示统计面板（可视化图表）
8. 展示操作日志
9. 展示优惠券转赠流程
10. 展示数据导出

---

## 九、AI 调用方式

参考已有 `bedrock.service.ts` 实现：

```typescript
// 支持两种调用方式
// 1. SDK 凭证模式：BedrockRuntimeClient + ConverseCommand
// 2. API Key 模式：HTTP POST + Bearer Token

// 模型列表动态获取
// 运行时可选择具体模型
// 超时处理、错误降级完善
```

关键设计：
- 前端提供模型选择配置
- 后端封装统一的 AI 调用服务
- AI 不可用时自动降级为规则引擎
- 支持超时处理和错误重试

---

## 十、环境变量与配置

项目运行需要的环境配置（`.env.local` 文件）：

```bash
# 数据库
DATABASE_URL="file:./dev.db"

# JWT 认证
JWT_SECRET="your-jwt-secret-key"
JWT_EXPIRES_IN="7d"

# AWS Bedrock - SDK 模式（二选一）
AWS_REGION="us-east-1"
AWS_ACCESS_KEY_ID="your-access-key"
AWS_SECRET_ACCESS_KEY="your-secret-key"

# AWS Bedrock - API Key 模式（二选一）
BEDROCK_API_KEY="your-bedrock-api-key"
BEDROCK_REGION="us-east-1"

# 默认AI模型（可在前端页面切换）
DEFAULT_MODEL_ID="anthropic.claude-3-sonnet-20240229-v1:0"

# 应用配置
NEXT_PUBLIC_APP_NAME="优惠券中心"
```

---

## 十一、风控规则引擎（AI降级方案）

当 AI 服务不可用时，系统自动降级为以下规则引擎：

| 规则编号 | 规则名称 | 触发条件 | 决策 |
|----------|----------|----------|------|
| R-1 | 高频领取 | 同一用户10秒内请求超过50次 | 拦截 |
| R-2 | 短时集中领取 | 同一用户1分钟内领取超过10张不同券 | 人工审核 |
| R-3 | 新账号异常 | 注册不足5分钟即开始批量领券 | 人工审核 |
| R-4 | IP异常 | 同一IP短时间注册多个账号并领券 | 拦截 |
| R-5 | 黑名单用户 | 用户在黑名单中 | 拦截 |
| R-6 | 白名单豁免 | 用户在白名单中 | 放行（跳过风控） |

风控输出格式：
```json
{
  "score": 85,
  "decision": "block",
  "reason": "10秒内领取请求达52次，触发高频领取规则",
  "rule": "R-1",
  "timestamp": "2026-07-29T10:00:00Z"
}
```

---

## 十二、数据模型概要

### 核心实体

- **User**：用户（id, username, password_hash, role, created_at）
- **Campaign**：活动（id, name, type, params, stock, limit_per_user, start_time, end_time, validity_days, shareable, share_limit, transferable, stackable, created_by, template_id）
- **Coupon**：优惠券实例（id, coupon_code, campaign_id, user_id, status, claimed_at, used_at, expires_at, transferred_from）
- **Redemption**：核销记录（id, coupon_id, coupon_code, redeemed_by, redeemed_at）
- **ShareLink**：分享链接（id, campaign_id, created_by, share_code, max_claims, current_claims, expires_at, created_at）
- **RiskLog**：风控记录（id, user_id, action, score, decision, reason, rule_triggered, ai_explanation, created_at）
- **OperationLog**：操作日志（id, user_id, action, target, detail, created_at）
- **Notification**：通知（id, user_id, type, content, read, created_at）
- **Blacklist/Whitelist**：黑白名单（id, user_id, type, reason, created_by, created_at）
- **CampaignTemplate**：活动模板（id, name, config, created_by, created_at）
- **Favorite**：收藏（id, user_id, campaign_id, created_at）

### 优惠券状态流转

```
[未领取] → 领取 → [已领取/待使用] → 核销 → [已核销]
                         ↓                    
                      转赠 → [已转赠] → 对方获得[已领取/待使用]
                         ↓
                      过期 → [已过期]
```

### 券码规则
- 每张优惠券实例有唯一券码（coupon_code）
- 格式：大写字母+数字，8-12位，如 `CPN-A3X9K2M7`
- 核销人员通过输入券码完成核销操作

---

## 十三、API 接口清单

### 认证
| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| POST | /api/auth/register | 注册 | 公开 |
| POST | /api/auth/login | 登录 | 公开 |
| GET | /api/auth/me | 获取当前用户信息 | 已登录 |

### 活动管理
| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| GET | /api/campaigns | 获取活动列表 | 所有 |
| GET | /api/campaigns/:id | 获取活动详情 | 所有 |
| POST | /api/campaigns | 创建活动 | 运营 |
| PUT | /api/campaigns/:id | 编辑活动 | 运营 |
| DELETE | /api/campaigns/:id | 删除活动 | 运营 |
| POST | /api/campaigns/batch-send | 批量发券 | 运营 |

### 优惠券操作
| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| POST | /api/coupons/claim | 领取优惠券 | 用户 |
| GET | /api/coupons/my | 我的券包 | 用户 |
| POST | /api/coupons/transfer | 转赠优惠券 | 用户 |
| POST | /api/coupons/share | 生成分享链接 | 用户 |
| POST | /api/coupons/claim-share/:code | 通过分享链接领券 | 用户 |
| GET | /api/coupons/ranking | 优惠券排行榜 | 所有 |

### 核销
| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| POST | /api/redeem | 核销（输入券码） | 核销人员 |
| GET | /api/redeem/records | 核销记录 | 核销人员 |

### AI服务
| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| POST | /api/ai/recommend | 智能推券 | 用户 |
| POST | /api/ai/risk-check | 风控检测 | 系统内部 |
| POST | /api/ai/generate-copy | AI文案生成 | 运营 |
| GET | /api/ai/user-profile/:id | AI用户画像 | 管理员 |
| GET | /api/ai/models | 获取可用模型列表 | 管理员 |

### 统计与管理
| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| GET | /api/stats/overview | 统计概览 | 管理员 |
| GET | /api/stats/export | 数据导出 | 管理员 |
| GET | /api/logs | 操作日志 | 管理员 |
| GET | /api/notifications | 通知列表 | 已登录 |
| PUT | /api/notifications/:id/read | 标记已读 | 已登录 |

### 黑白名单与收藏
| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| GET | /api/blacklist | 获取黑白名单 | 运营 |
| POST | /api/blacklist | 添加黑/白名单 | 运营 |
| DELETE | /api/blacklist/:id | 移除黑/白名单 | 运营 |
| GET | /api/favorites | 收藏列表 | 用户 |
| POST | /api/favorites | 添加收藏 | 用户 |
| DELETE | /api/favorites/:id | 取消收藏 | 用户 |

### 模板
| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| GET | /api/templates | 获取模板列表 | 运营 |
| POST | /api/templates | 保存模板 | 运营 |
| DELETE | /api/templates/:id | 删除模板 | 运营 |

---

## 十四、页面结构

```
/ (首页/登录)
├── /register (注册 - 选角色)
├── /login (登录)
├── /user (普通用户)
│   ├── /coupons (我的券包)
│   ├── /explore (浏览/领券)
│   ├── /favorites (收藏夹)
│   ├── /notifications (通知)
│   └── /ranking (排行榜)
├── /operator (运营人员)
│   ├── /campaigns (活动管理)
│   ├── /create (创建活动 + AI文案)
│   ├── /templates (活动模板)
│   ├── /batch (批量发券)
│   └── /blacklist (黑白名单)
├── /verifier (核销人员)
│   ├── /verify (核销操作)
│   └── /records (核销记录)
└── /admin (管理员)
    ├── /dashboard (统计面板 + 图表)
    ├── /logs (操作日志)
    ├── /export (数据导出)
    └── /risk (风控监控)
```

---

## 十五、项目结构（预期）

```
coupon-center/
├── app/                    # Next.js App Router
│   ├── api/               # API Routes (后端接口)
│   │   ├── auth/          # 注册/登录
│   │   ├── campaigns/     # 活动管理
│   │   ├── coupons/       # 优惠券操作
│   │   ├── redeem/        # 核销
│   │   ├── ai/            # AI相关接口
│   │   ├── stats/         # 统计
│   │   ├── logs/          # 操作日志
│   │   └── notifications/ # 通知
│   ├── (auth)/            # 认证相关页面
│   ├── user/              # 普通用户页面
│   ├── operator/          # 运营人员页面
│   ├── verifier/          # 核销人员页面
│   └── admin/             # 管理员页面
├── components/            # 通用组件
├── lib/                   # 工具库
│   ├── db.ts             # 数据库连接
│   ├── auth.ts           # 认证工具
│   ├── bedrock.ts        # AI服务 (参考bedrock.service.ts)
│   └── risk-engine.ts    # 风控引擎
├── prisma/               # Prisma Schema & Migrations
├── public/               # 静态资源
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── next.config.js
```

---

## 十六、可用Skill

| Skill | 用途 | 本项目是否使用 |
|-------|------|---------------|
| demo-dev-ui-builder | Next.js开发UI脚手架 | 可参考模板结构 |
| aws-remote-deploy | AWS部署脚本 | 本项目暂不使用（纯本地运行） |

---

## 十七、开发优先级

### P0 - 核心必须（MVP）
1. 用户注册/登录/角色权限
2. 活动创建/编辑（7种优惠券类型）
3. 用户领券（库存扣减、限领校验）
4. 核销管理（幂等、过期校验）
5. AI智能推券
6. AI异常检测/风控

### P1 - 重要功能
7. 统计面板 + 可视化图表
8. AI智能文案生成
9. AI异常行为解释
10. 操作日志
11. 数据导出

### P2 - 增强体验
12. 优惠券转赠
13. 分享领券
14. 优惠券收藏夹
15. 领券进度条
16. 优惠券排行榜
17. 通知消息
18. 活动模板
19. 批量发券
20. 黑白名单
21. AI用户画像分析
22. 叠加使用规则
