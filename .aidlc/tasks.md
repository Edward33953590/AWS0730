# 实现任务列表

**审阅状态**：已认可
**认可日期**：2026-07-29
**认可来源**：用户确认"逐个实现吧"
**范围基线**：FR-001~FR-024, NFR-001~NFR-010
**最近审阅记录**：无

---

## T-001 项目初始化与基础配置

- [ ] 完成

**目标**：搭建Next.js项目脚手架，配置所有基础依赖和开发环境

**范围**：
- 创建Next.js 14项目（App Router）
- 安装全部依赖（见technology-stack.md）
- 配置TailwindCSS、TypeScript、ESLint
- 创建.env.example模板
- 配置项目目录结构

**不包含**：业务代码、数据库表、页面

**Depends on**：无

**需求引用**：NFR-007, NFR-010

**设计引用**：technology-stack.md, system-architecture.md（项目结构）

**实现要点**：
- `npx create-next-app@14` 初始化
- 安装依赖列表参考 technology-stack.md
- 创建lib/、components/目录结构
- .env.example包含所有环境变量

**验收标准**：
- `npm run dev` 启动成功，localhost:3000可访问
- TypeScript编译无错误
- TailwindCSS样式生效

**验证命令**：`npm run build`

**交付物**：完整的项目脚手架，可启动运行

---

## T-002 数据库Schema与种子数据

- [ ] 完成

**目标**：定义Prisma Schema，创建所有数据库表，填充种子数据

**范围**：
- 定义prisma/schema.prisma（11张表+枚举）
- 配置SQLite连接
- 创建种子脚本（预置各角色测试账号+示例活动）
- SQLite WAL模式配置

**不包含**：业务逻辑代码

**Depends on**：T-001

**需求引用**：FR-001~FR-024（数据基础）

**设计引用**：database-design.md

**实现要点**：
- 严格按database-design.md定义表结构
- 枚举类型：Role, CouponType, ValidityMode, CouponStatus, RiskDecision, ListType
- 种子数据：admin/operator/verifier/user各1个测试账号
- 种子数据：2-3个示例活动

**验收标准**：
- `npx prisma db push` 成功创建表
- `npx prisma db seed` 成功填充种子数据
- Prisma Studio可查看数据

**验证命令**：`npx prisma db push ; npx prisma db seed`

**交付物**：prisma/schema.prisma, prisma/seed.ts

---

## T-003 认证系统（注册/登录/JWT中间件）

- [ ] 完成

**目标**：实现用户注册、登录、JWT认证中间件和角色权限守卫

**范围**：
- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me
- JWT签发/验证工具函数（lib/auth.ts）
- 角色权限中间件

**不包含**：前端页面

**Depends on**：T-002

**需求引用**：FR-001, FR-002, NFR-005

**设计引用**：api-specification.md（认证接口）, system-architecture.md（安全边界）

**实现要点**：
- bcryptjs哈希密码（salt rounds=10）
- jose签发JWT（含userId, role, exp）
- 中间件提取token验证，注入user到请求
- 角色守卫函数：requireRole('ADMIN', 'OPERATOR')
- 用户名唯一校验

**验收标准**：
- 注册成功返回token
- 重复用户名返回409
- 登录成功返回token
- 错误密码返回401
- /api/auth/me携带token返回用户信息
- 无token请求受保护接口返回401

**验证命令**：curl测试注册→登录→me接口

**交付物**：app/api/auth/*/route.ts, lib/auth.ts

---

## T-004 活动管理API

- [ ] 完成

**目标**：实现活动的CRUD接口

**范围**：
- GET /api/campaigns（列表+分页+筛选）
- GET /api/campaigns/:id
- POST /api/campaigns（创建，含类型参数校验+默认值）
- PUT /api/campaigns/:id（编辑，库存只增不减）
- DELETE /api/campaigns/:id

**不包含**：批量发券、模板、AI文案

**Depends on**：T-003

**需求引用**：FR-003, FR-004

**设计引用**：api-specification.md（活动管理接口）, database-design.md（Campaign表）

**实现要点**：
- 7种优惠券类型参数校验
- 默认值填充逻辑
- 库存编辑约束（不低于已发放数）
- 运营人员角色权限校验
- 分页查询

**验收标准**：
- 运营可创建7种类型活动
- 选择类型后默认值正确
- 非运营角色创建返回403
- 编辑库存低于已发放数被拒绝

**验证命令**：curl测试CRUD接口

**交付物**：app/api/campaigns/*/route.ts, lib/services/campaign.ts

---

## T-005 领券核心逻辑（并发安全）

- [ ] 完成

**目标**：实现用户领取优惠券的核心逻辑，保证并发安全

**范围**：
- POST /api/coupons/claim
- 库存原子扣减（事务+条件WHERE）
- 限领校验
- 券码生成（CPN-XXXXXXXX）
- 有效期计算（两种模式）
- 新人券、限时券校验

**不包含**：风控检测（T-008）、AI推荐（T-009）

**Depends on**：T-004

**需求引用**：FR-005, NFR-001, NFR-006

**设计引用**：api-specification.md（领券接口）, database-design.md（Coupon表+Campaign约束）

**实现要点**：
- Prisma事务：UPDATE Campaign SET remainingStock = remainingStock - 1 WHERE remainingStock > 0
- 同一事务内检查用户已领数量
- 券码生成：CPN- + 8位随机大写字母数字
- 有效期：RELATIVE模式=claimedAt+validityDays, FIXED模式=fixedEndDate

**验收标准**：
- 库存为1时，2个并发请求只有1个成功
- 同一用户超限领数返回409 ALREADY_CLAIMED
- 活动未开始/已结束正确拒绝
- 券码格式正确且唯一

**验证命令**：并发curl测试

**交付物**：app/api/coupons/claim/route.ts, lib/services/coupon.ts

---

## T-006 核销接口（幂等）

- [ ] 完成

**目标**：实现优惠券核销接口，保证幂等性

**范围**：
- POST /api/redeem（输入券码核销）
- GET /api/redeem/records（核销记录查询）
- 幂等处理
- 过期/状态校验

**不包含**：叠加规则校验（P2功能）

**Depends on**：T-005

**需求引用**：FR-006, NFR-002

**设计引用**：api-specification.md（核销接口）, database-design.md（Redemption表）

**实现要点**：
- 查询Coupon by couponCode
- 状态检查：CLAIMED才可核销
- 过期检查：expiresAt < now() 拒绝
- 已核销：返回首次核销信息（幂等）
- 核销人员角色校验
- 创建Redemption记录 + 更新Coupon状态

**验收标准**：
- 有效券码核销成功
- 无效券码返回404
- 过期券返回410
- 已核销券返回409+首次核销信息（幂等）
- 非核销人员返回403

**验证命令**：curl测试正常/重复/过期核销

**交付物**：app/api/redeem/route.ts, lib/services/redemption.ts

---

## T-007 操作日志服务

- [ ] 完成

**目标**：实现操作日志记录和查询

**范围**：
- 日志记录函数（可在其他服务中调用）
- GET /api/logs（管理员查询+筛选+分页）
- 在T-005领券和T-006核销中集成日志

**不包含**：前端页面

**Depends on**：T-005, T-006

**需求引用**：FR-013

**设计引用**：database-design.md（OperationLog表）, api-specification.md（日志接口）

**实现要点**：
- logOperation(userId, action, target, detail) 工具函数
- 异步写入（不影响主流程性能）
- 查询支持：action筛选、userId筛选、时间范围、分页

**验收标准**：
- 领券操作有日志记录
- 核销操作有日志记录
- 管理员可查询日志列表
- 筛选功能正常

**验证命令**：领券后查询日志接口

**交付物**：lib/services/log.ts, app/api/logs/route.ts

---

## T-008 风控引擎（AI+规则降级）

- [ ] 完成

**目标**：实现风控检测系统，含AI评估和规则引擎降级

**范围**：
- POST /api/ai/risk-check
- AI风控：调用Bedrock评估行为
- 规则引擎降级：6条规则(R-1~R-6)
- 频率统计（内存计数器）
- 黑白名单检查
- 集成到领券流程（T-005调用风控）
- RiskLog记录

**不包含**：AI异常解释（含在AI响应中）、风控仪表盘前端

**Depends on**：T-005, T-007

**需求引用**：FR-008, NFR-004

**设计引用**：system-architecture.md（AI降级）, setup.md（风控规则）

**实现要点**：
- BedrockService封装（参考bedrock.service.ts）
- 风控prompt设计：传入用户行为数据，返回评分+决策+理由
- 内存Map统计请求频率（简单实现）
- try-catch自动降级
- 降级后使用规则引擎

**验收标准**：
- 10秒50次请求触发拦截
- AI正常时返回评分+决策+AI解释
- AI超时/错误时自动降级为规则引擎
- 黑名单用户直接拦截
- 白名单用户跳过风控
- RiskLog有记录

**验证命令**：快速循环curl测试触发风控

**交付物**：lib/services/bedrock.ts, lib/services/risk-engine.ts, app/api/ai/risk-check/route.ts

---

## T-009 AI智能推券

- [ ] 完成

**目标**：实现AI个性化推荐接口

**范围**：
- POST /api/ai/recommend
- Bedrock调用：传入用户历史，返回推荐+理由
- 降级方案：热门券列表

**不包含**：前端UI

**Depends on**：T-008（复用BedrockService）

**需求引用**：FR-007, NFR-004

**设计引用**：api-specification.md（AI推荐接口）

**实现要点**：
- 收集用户历史：领券记录、核销记录
- prompt设计：含活动列表+用户历史，要求返回JSON推荐列表+理由
- 降级：AI失败时按领取量排序返回热门券
- 响应标记source: "ai" | "fallback"

**验收标准**：
- 返回非空推荐列表
- 每条推荐有理由文本
- AI不可用时返回热门券（source=fallback）

**验证命令**：curl测试推荐接口

**交付物**：app/api/ai/recommend/route.ts

---

## T-010 AI文案生成

- [ ] 完成

**目标**：实现运营创建活动时的AI文案生成

**范围**：
- POST /api/ai/generate-copy
- 降级：预设模板文案

**不包含**：前端集成

**Depends on**：T-008（复用BedrockService）

**需求引用**：FR-011, NFR-004

**设计引用**：api-specification.md（文案生成接口）

**实现要点**：
- 输入：类型+参数+场景描述
- prompt要求返回：title, description, slogan
- 降级：根据类型返回预设模板文案

**验收标准**：
- 返回标题+描述+话术
- 内容与类型/面额相关
- AI不可用时返回预设文案

**验证命令**：curl测试文案生成接口

**交付物**：app/api/ai/generate-copy/route.ts

---

## T-011 前端布局与认证页面

- [ ] 完成

**目标**：实现前端全局布局、登录页、注册页和认证状态管理

**范围**：
- 全局Layout（Header+导航+铃铛+用户菜单）
- /login 登录页面
- /register 注册页面（含角色下拉）
- AuthContext（JWT存储、用户状态）
- 路由守卫（未登录跳转login）
- 角色路由守卫

**不包含**：各角色的功能页面

**Depends on**：T-003

**需求引用**：FR-001, FR-002, NFR-009

**设计引用**：frontend-design.md（2.1全局布局, 2.2登录注册）

**实现要点**：
- AuthContext: login/logout/user state
- JWT存localStorage
- Header根据角色显示不同导航
- 表单校验：用户名3-20字符，密码6-50字符
- 美观UI：居中卡片、TailwindCSS

**验收标准**：
- 注册成功自动跳转角色首页
- 登录成功跳转角色首页
- 未登录访问功能页跳转login
- 角色不匹配跳转自己的首页
- UI美观

**验证命令**：浏览器手动测试

**交付物**：app/layout.tsx, app/login/page.tsx, app/register/page.tsx, lib/auth-context.tsx, components/Header.tsx

---

## T-012 用户端页面（领券+券包+推荐）

- [ ] 完成

**目标**：实现普通用户的核心页面

**范围**：
- /user 首页（AI推荐区+热门券）
- /user/explore 浏览所有活动（筛选+进度条+领取按钮）
- /user/coupons 我的券包（券码展示+状态）
- CouponCard组件（进度条+类型标签+收藏+领取+分享）

**不包含**：收藏夹、排行榜、通知、转赠（后续任务）

**Depends on**：T-011, T-005, T-009

**需求引用**：FR-005, FR-007, FR-017, NFR-009

**设计引用**：frontend-design.md（2.3用户首页）

**实现要点**：
- AI推荐区：自动加载+刷新按钮+推荐理由展示
- 活动列表：卡片布局、类型筛选、进度条
- 领取按钮：loading状态、成功toast、错误提示
- 券包：展示券码、状态、有效期

**验收标准**：
- AI推荐正常展示（含理由）
- 领取操作正常（成功/失败提示）
- 进度条百分比正确
- 券包展示已领券的券码和状态

**验证命令**：浏览器手动测试完整领券流程

**交付物**：app/user/*/page.tsx, components/CouponCard.tsx

---

## T-013 运营端页面（活动管理+AI文案）

- [ ] 完成

**目标**：实现运营人员的活动管理页面

**范围**：
- /operator 运营首页（活动概览）
- /operator/campaigns 活动列表
- /operator/campaigns/create 创建活动（含AI文案按钮+默认值+类型切换）
- /operator/campaigns/:id 编辑活动

**不包含**：模板、批量发券、黑白名单

**Depends on**：T-011, T-004, T-010

**需求引用**：FR-003, FR-004, FR-011, NFR-009

**设计引用**：frontend-design.md（2.4运营创建页面）

**实现要点**：
- 类型选择后自动填充默认参数
- AI文案生成按钮+loading+结果预览
- 高级设置折叠（转赠/叠加/分享）
- 活动列表：状态标签、库存显示、编辑/删除

**验收标准**：
- 7种类型创建均正常
- 默认值正确填充
- AI文案生成展示在表单中
- 编辑活动正常

**验证命令**：浏览器手动测试创建+编辑活动

**交付物**：app/operator/*/page.tsx

---

## T-014 核销端页面

- [ ] 完成

**目标**：实现核销人员的核销操作和记录页面

**范围**：
- /verifier 核销首页
- /verifier/verify 核销页面（输入框+按钮+结果展示）
- /verifier/records 核销记录列表

**不包含**：无

**Depends on**：T-011, T-006

**需求引用**：FR-006, NFR-009

**设计引用**：frontend-design.md（2.5核销页面）

**实现要点**：
- 输入券码输入框+大号核销按钮
- 核销结果展示（成功/失败/过期/已核销，不同颜色）
- 最近核销记录列表（实时更新）

**验收标准**：
- 输入有效券码核销成功+展示信息
- 无效/过期/已核销有对应错误展示
- 核销记录列表正确

**验证命令**：浏览器测试完整核销流程

**交付物**：app/verifier/*/page.tsx

---

## T-015 管理员统计面板+数据导出

- [ ] 完成

**目标**：实现管理员统计面板（图表可视化）和数据导出

**范围**：
- GET /api/stats/overview（统计聚合接口）
- GET /api/stats/export（数据导出接口）
- /admin/dashboard 统计面板页面（图表）
- /admin/export 数据导出页面
- Recharts图表：折线图、柱状图、饼图

**不包含**：操作日志页面、风控页面

**Depends on**：T-011, T-007

**需求引用**：FR-009, FR-010, NFR-009

**设计引用**：frontend-design.md（2.6统计面板）, api-specification.md（统计接口）

**实现要点**：
- 统计接口：聚合领取率、核销率、库存、活动数
- 图表数据：日领取趋势、类型分布饼图、核销趋势
- 数据卡片（大数字展示）
- 导出：CSV/Excel格式，xlsx库生成

**验收标准**：
- 统计数字准确
- 图表正常渲染+可交互
- 导出文件可正常打开

**验证命令**：浏览器查看面板+下载导出文件

**交付物**：app/api/stats/*/route.ts, app/admin/dashboard/page.tsx, app/admin/export/page.tsx, lib/services/stats.ts

---

## T-016 通知系统

- [ ] 完成

**目标**：实现站内通知系统（铃铛+消息列表+未读数）

**范围**：
- GET /api/notifications
- PUT /api/notifications/:id/read
- PUT /api/notifications/read-all
- 通知创建工具函数
- 铃铛组件（Header中）
- /user/notifications 通知列表页
- 集成：领券成功、转赠、风控拦截时创建通知

**不包含**：过期提醒（需定时任务，可后续加）

**Depends on**：T-011, T-005

**需求引用**：FR-019

**设计引用**：frontend-design.md（NotificationBell组件）, database-design.md（Notification表）

**实现要点**：
- createNotification(userId, type, content) 工具函数
- 在领券成功后调用
- Header铃铛显示未读数
- 点击铃铛展开通知面板或跳转通知页
- 标记已读/全部已读

**验收标准**：
- 领券后有通知
- 铃铛显示未读数
- 标记已读后未读数减少

**验证命令**：浏览器测试领券后查看通知

**交付物**：lib/services/notification.ts, app/api/notifications/*/route.ts, components/NotificationBell.tsx, app/user/notifications/page.tsx

---

## T-017 转赠与分享领券

- [ ] 完成

**目标**：实现优惠券转赠和分享链接领券

**范围**：
- POST /api/coupons/transfer
- POST /api/coupons/share
- POST /api/coupons/claim-share/:code
- /share/:code 分享领券页面
- 券包中转赠按钮
- 转赠/分享通知集成

**不包含**：无

**Depends on**：T-005, T-016

**需求引用**：FR-014, FR-015

**设计引用**：api-specification.md（转赠/分享接口）, database-design.md（ShareLink表）

**实现要点**：
- 转赠：状态变TRANSFERRED，新建一条CLAIMED给目标用户
- 分享：生成ShareLink记录，shareCode唯一
- 分享领取：检查currentClaims < maxClaims
- 通知双方

**验收标准**：
- 转赠后原用户券消失，目标用户获得
- 不可转赠的券提示
- 分享链接可领取
- 超出分享次数后失败

**验证命令**：浏览器测试转赠+分享流程

**交付物**：app/api/coupons/transfer/route.ts, app/api/coupons/share/route.ts, app/api/coupons/claim-share/[code]/route.ts, app/share/[code]/page.tsx

---

## T-018 收藏夹与排行榜

- [ ] 完成

**目标**：实现优惠券收藏和排行榜

**范围**：
- GET/POST/DELETE /api/favorites
- GET /api/coupons/ranking
- /user/favorites 收藏夹页面
- /user/ranking 排行榜页面
- CouponCard收藏按钮集成

**不包含**：无

**Depends on**：T-012

**需求引用**：FR-016, FR-018

**设计引用**：database-design.md（Favorite表）, api-specification.md

**实现要点**：
- 收藏幂等（已收藏不报错）
- 排行榜：按已领取数DESC排序，取TOP 10
- CouponCard心形图标切换

**验收标准**：
- 收藏/取消收藏正常
- 收藏夹页面展示正确
- 排行榜排序正确

**验证命令**：浏览器测试收藏+排行榜

**交付物**：app/api/favorites/*/route.ts, app/api/coupons/ranking/route.ts, app/user/favorites/page.tsx, app/user/ranking/page.tsx

---

## T-019 活动模板与批量发券

- [ ] 完成

**目标**：实现活动模板CRUD和批量发券功能

**范围**：
- GET/POST/DELETE /api/templates
- POST /api/campaigns/batch-send
- /operator/templates 模板管理页面
- /operator/batch 批量发券页面
- 创建活动时"保存为模板"和"从模板加载"

**不包含**：无

**Depends on**：T-013

**需求引用**：FR-020, FR-021

**设计引用**：api-specification.md（模板/批量接口）, database-design.md（CampaignTemplate表）

**实现要点**：
- 模板保存完整活动配置为JSON
- 从模板加载：填充表单
- 批量发券：选活动+选用户列表，循环创建Coupon
- 库存校验、跳过已超限领用户

**验收标准**：
- 模板保存/加载参数一致
- 批量发券成功，库存正确扣减
- 超限领用户被跳过

**验证命令**：浏览器测试模板+批量发券

**交付物**：app/api/templates/*/route.ts, app/api/campaigns/batch-send/route.ts, app/operator/templates/page.tsx, app/operator/batch/page.tsx

---

## T-020 黑白名单管理

- [ ] 完成

**目标**：实现运营人员的黑白名单管理

**范围**：
- GET/POST/DELETE /api/blacklist
- /operator/blacklist 黑白名单页面
- 与风控引擎集成（T-008已实现查询逻辑）

**不包含**：无

**Depends on**：T-008, T-013

**需求引用**：FR-022

**设计引用**：database-design.md（BlackWhiteList表）, api-specification.md

**实现要点**：
- 添加时需填写原因
- userId+type联合唯一
- 列表展示+删除
- 风控引擎中已有黑白名单检查逻辑

**验收标准**：
- 添加黑名单用户后该用户无法领券
- 添加白名单用户后该用户跳过风控
- 删除名单后恢复正常

**验证命令**：添加黑名单→尝试领券→被拒绝

**交付物**：app/api/blacklist/*/route.ts, app/operator/blacklist/page.tsx, lib/services/blacklist.ts

---

## T-021 管理员日志与风控页面

- [ ] 完成

**目标**：实现管理员的操作日志和风控监控页面

**范围**：
- /admin/logs 操作日志页面（表格+筛选）
- /admin/risk 风控监控页面（拦截记录+AI解释展示）

**不包含**：无

**Depends on**：T-015, T-007, T-008

**需求引用**：FR-012, FR-013

**设计引用**：frontend-design.md（管理员页面）

**实现要点**：
- 日志页面：DataTable组件+筛选器（时间/类型/用户）
- 风控页面：展示RiskLog记录，AI解释文本高亮
- 风控统计：拦截数、审核数

**验收标准**：
- 日志列表+筛选正常
- 风控记录展示AI解释文本
- 分页正常

**验证命令**：浏览器查看日志+风控页面

**交付物**：app/admin/logs/page.tsx, app/admin/risk/page.tsx

---

## T-022 AI用户画像

- [ ] 完成

**目标**：实现AI用户画像分析功能

**范围**：
- GET /api/ai/user-profile/:userId
- /admin/profiles 用户画像页面
- 降级：基础规则标签

**不包含**：无

**Depends on**：T-008, T-021

**需求引用**：FR-023, NFR-004

**设计引用**：api-specification.md（用户画像接口）

**实现要点**：
- 收集用户数据：领券类型偏好、频率、核销率
- Bedrock prompt：分析用户行为，返回标签+描述
- 降级：根据数据规则生成基础标签

**验收标准**：
- 返回用户标签列表+描述
- 标签与用户行为相关
- AI不可用时返回规则标签

**验证命令**：curl测试画像接口

**交付物**：app/api/ai/user-profile/[userId]/route.ts, app/admin/profiles/page.tsx

---

## T-023 叠加规则与我的券包增强

- [ ] 完成

**目标**：实现优惠券叠加使用规则和券包页面增强

**范围**：
- 核销时叠加校验逻辑
- GET /api/coupons/my 增强（展示更多信息）
- 券包页面增强：转赠按钮、状态筛选

**不包含**：无

**Depends on**：T-006, T-017

**需求引用**：FR-024

**设计引用**：database-design.md（Campaign.stackable）

**实现要点**：
- 核销时检查：如果券不可叠加，检查该用户当天是否已核销其他不可叠加券
- 券包筛选：全部/待使用/已核销/已过期/已转赠

**验收标准**：
- 不可叠加券同一天只能核销一张
- 可叠加券无此限制
- 券包筛选正常

**验证命令**：测试叠加限制

**交付物**：更新redemption.ts逻辑, 更新app/user/coupons/page.tsx

---

## T-024 UI美化与演示优化

- [ ] 完成

**目标**：整体UI美化，确保演示效果好

**范围**：
- 全局样式统一和美化
- 加载状态和空状态组件
- AI操作的loading动画
- 响应式适配
- 错误处理统一
- Toast通知样式
- 首页欢迎/引导

**不包含**：新功能

**Depends on**：T-012~T-022

**需求引用**：NFR-009

**设计引用**：frontend-design.md（视觉风格、交互规范）

**实现要点**：
- 统一配色（蓝色系主色调）
- 所有按钮加loading状态
- AI操作骨架屏/脉冲动画
- 空状态插画/提示
- 移动端基本适配
- 错误边界（Error Boundary）

**验收标准**：
- 界面整体美观统一
- 所有操作有加载/成功/失败反馈
- 无明显UI错位或不一致

**验证命令**：浏览器全流程走查

**交付物**：components/*, app/globals.css优化

---

## T-025 端到端演示验证

- [ ] 完成

**目标**：按竞赛演示流程完整验证系统

**范围**：
- 按竞赛演示流程执行全部步骤
- 修复发现的问题
- 确保种子数据适合演示
- 编写简要启动和演示指南

**不包含**：新功能开发

**Depends on**：T-024

**需求引用**：AC-1~AC-10, NFR-009

**设计引用**：setup.md（第八节竞赛演示流程）

**实现要点**：
- 演示流程：
  1. 运营创建库存1的活动（AI文案）
  2. 用户A领取成功（AI推荐）
  3. 用户B领取失败（库存不足）
  4. 用户A核销成功
  5. 用户A再次核销（幂等）
  6. 用户C高频领取（风控拦截+AI解释）
  7. 统计面板+数据导出
  8. 操作日志
  9. 转赠流程
- 修复演示中发现的任何问题

**验收标准**：
- 竞赛演示流程全部通过
- 种子数据合理
- 有启动指南

**验证命令**：完整演示流程走查

**交付物**：更新prisma/seed.ts, 创建README.md（启动指南）
