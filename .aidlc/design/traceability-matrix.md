# 追踪矩阵

## 功能需求 → 设计映射

| 需求 | 数据实体 | API接口 | 前端页面 | 服务模块 | 验证方式 |
|------|----------|---------|----------|----------|----------|
| FR-001 用户注册 | User | POST /api/auth/register | /register | AuthService | 注册+登录成功 |
| FR-002 用户登录 | User | POST /api/auth/login | /login | AuthService | 登录后权限生效 |
| FR-003 活动创建 | Campaign | POST /api/campaigns | /operator/campaigns/create | CampaignService | 创建后列表可见 |
| FR-004 活动编辑 | Campaign | PUT /api/campaigns/:id | /operator/campaigns/:id | CampaignService | 编辑后参数更新 |
| FR-005 用户领券 | Coupon, Campaign | POST /api/coupons/claim | /user/explore | CouponService | 并发+限领测试 |
| FR-006 核销 | Coupon, Redemption | POST /api/redeem | /verifier/verify | RedemptionService | 幂等+过期测试 |
| FR-007 AI推券 | - | POST /api/ai/recommend | /user (首页推荐区) | BedrockService | 非空列表+理由 |
| FR-008 AI风控 | RiskLog | POST /api/ai/risk-check | (内部调用) | RiskEngine | 高频拦截测试 |
| FR-009 统计面板 | (聚合查询) | GET /api/stats/overview | /admin/dashboard | StatsService | 数据准确+图表 |
| FR-010 数据导出 | (聚合查询) | GET /api/stats/export | /admin/export | StatsService | 文件下载验证 |
| FR-011 AI文案 | - | POST /api/ai/generate-copy | /operator/campaigns/create | BedrockService | 生成文案有效 |
| FR-012 AI异常解释 | RiskLog | (含在risk-check中) | /admin/risk | BedrockService | 解释文本可读 |
| FR-013 操作日志 | OperationLog | GET /api/logs | /admin/logs | LogService | 操作有记录 |
| FR-014 转赠 | Coupon | POST /api/coupons/transfer | /user/coupons | CouponService | 归属变更正确 |
| FR-015 分享领券 | ShareLink | POST /api/coupons/share | /user/explore, /share/:code | ShareService | 次数限制生效 |
| FR-016 收藏夹 | Favorite | GET/POST/DEL /api/favorites | /user/favorites | FavoriteService | 收藏/取消正常 |
| FR-017 进度条 | Campaign | (含在campaigns列表) | /user/explore | - | 百分比准确 |
| FR-018 排行榜 | (聚合查询) | GET /api/coupons/ranking | /user/ranking | StatsService | 排序正确 |
| FR-019 通知 | Notification | GET/PUT /api/notifications | 全局Header铃铛 | NotificationService | 通知触发正确 |
| FR-020 活动模板 | CampaignTemplate | GET/POST/DEL /api/templates | /operator/templates | TemplateService | 加载参数一致 |
| FR-021 批量发券 | Coupon | POST /api/campaigns/batch-send | /operator/batch | CouponService | 批量发放成功 |
| FR-022 黑白名单 | BlackWhiteList | GET/POST/DEL /api/blacklist | /operator/blacklist | BlacklistService | 黑名单禁领 |
| FR-023 AI画像 | - | GET /api/ai/user-profile/:id | /admin/profiles | BedrockService | 标签相关 |
| FR-024 叠加规则 | Campaign.stackable | (含在redeem逻辑) | (核销时校验) | RedemptionService | 不可叠加限制 |

## 非功能需求 → 设计映射

| 需求 | 设计对应 | 验证方式 |
|------|----------|----------|
| NFR-001 并发安全 | Campaign.remainingStock原子扣减（事务+条件WHERE） | 并发压测N+1请求 |
| NFR-002 幂等性 | Redemption.couponId UNIQUE + 状态检查 | 重复核销测试 |
| NFR-003 响应时间 | AI接口超时设置(10s/15s) + 规则引擎<100ms | 接口计时 |
| NFR-004 AI降级 | BedrockService try-catch + fallback逻辑 | 模拟AI不可用 |
| NFR-005 安全性 | bcrypt + JWT + 角色中间件 + Prisma参数化 | 越权/注入测试 |
| NFR-006 数据一致性 | Prisma事务 + 状态机约束 | 数据核对 |
| NFR-007 可用性 | SQLite无外部依赖 + npm run dev一键启动 | 新环境启动 |
| NFR-008 可维护性 | TypeScript严格类型 + 模块化文件结构 | 代码审查 |
| NFR-009 演示友好 | 美观UI + 操作流畅 + AI输出可见 | 模拟演示 |
| NFR-010 环境配置 | .env.example + Prisma自动迁移 + seed | 新环境搭建 |

## 服务层模块清单

| 模块 | 文件路径 | 职责 |
|------|----------|------|
| AuthService | lib/services/auth.ts | 注册、登录、JWT签发验证 |
| CampaignService | lib/services/campaign.ts | 活动CRUD、参数校验 |
| CouponService | lib/services/coupon.ts | 领券、转赠、库存扣减 |
| RedemptionService | lib/services/redemption.ts | 核销、幂等、过期检查 |
| BedrockService | lib/services/bedrock.ts | AI调用封装（参考已有代码） |
| RiskEngine | lib/services/risk-engine.ts | 风控AI+规则引擎 |
| ShareService | lib/services/share.ts | 分享链接生成、领取 |
| StatsService | lib/services/stats.ts | 统计聚合、导出 |
| LogService | lib/services/log.ts | 操作日志记录 |
| NotificationService | lib/services/notification.ts | 通知创建、查询 |
| BlacklistService | lib/services/blacklist.ts | 黑白名单管理 |
| TemplateService | lib/services/template.ts | 活动模板CRUD |
