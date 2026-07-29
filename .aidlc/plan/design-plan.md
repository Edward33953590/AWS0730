# 设计计划

## 输入需求基线
- functional-requirements.md（24条FR）
- non-functional-requirements.md（10条NFR）
- user-stories.md（22条US）
- requirements-checklist.md（门禁已通过）
- setup.md（项目完整规划）
- bedrock.service.ts（AI调用参考实现）

## 设计步骤

- [x] 系统架构设计
- [x] 数据库设计
- [x] API接口设计
- [x] 前端设计
- [x] 技术栈文档
- [x] 追踪矩阵

## 技术决策记录 (ADR)

### ADR-001 选用Next.js App Router
- **决策**：使用Next.js 14 App Router（非Pages Router）
- **理由**：Server Components减少客户端JS、API Routes集成方便、文件系统路由直观
- **影响**：需区分Server/Client Components

### ADR-002 选用SQLite + Prisma
- **决策**：SQLite作为数据库，Prisma作为ORM
- **理由**：单机部署无需外部DB服务、Prisma类型安全+迁移管理、开发体验好
- **影响**：并发写入受SQLite限制（WAL模式可缓解）

### ADR-003 并发库存扣减方案
- **决策**：使用数据库事务 + 乐观锁（版本号/条件更新）
- **理由**：SQLite支持事务，条件UPDATE（stock > 0时扣减）保证原子性
- **影响**：高并发下可能有竞争重试，但单机演示场景足够

### ADR-004 JWT认证方案
- **决策**：自研JWT认证（jose库签发/验证）
- **理由**：简单直接、无需NextAuth复杂配置、全栈控制
- **影响**：需自行实现中间件和刷新逻辑

### ADR-005 AI服务封装
- **决策**：参考bedrock.service.ts封装统一AI服务层，支持SDK/API Key双模式
- **理由**：已有参考实现、灵活切换模型
- **影响**：需实现超时+降级逻辑

### ADR-006 前端图表库
- **决策**：使用Recharts
- **理由**：React原生、API简单、体积小、TailwindCSS兼容
- **影响**：无

## 阶段状态
- **状态**：已完成
- **完成日期**：2026-07-29
