# 需求分析计划

## 上下文与当前状态

- **项目名称**：优惠券发放与核销中心
- **项目来源**：SRCG Workshop 竞赛项目
- **当前阶段**：需求分析
- **已有产物**：setup.md（项目说明文档，已与用户确认完毕）
- **输入来源**：
  - `requirement/3.SRCG_workshop_Requirement.md`（原始需求）
  - `setup.md`（用户确认后的完整需求规划）
  - `goal/SRCG_workshop_competation_intro.md`（竞赛演示评比标准）
  - `bedrock.service.ts`（AI调用参考实现）

## 需求分析计划

- [x] 阅读原始需求文档
- [x] 与用户交互确认不明确的需求细节（8个主问题 + 2个补充问题）
- [x] 确认技术栈：Next.js + React + TailwindCSS + SQLite
- [x] 确认优惠券类型：7种
- [x] 确认用户系统：用户名+密码，注册选角色
- [x] 确认AI方案：参考bedrock.service.ts，双模式
- [x] 确认部署方式：本地运行
- [x] 确认扩展功能：16项
- [x] 生成 setup.md 项目说明文档
- [ ] 生成正式需求文档（functional/non-functional/user-stories/checklist）

## 问答记录

### Q-001
[Question]
技术栈选型？

[Answer]
A - Next.js全栈 + React + TailwindCSS + SQLite (Prisma ORM)

### Q-002
[Question]
优惠券类型选择？

[Answer]
全选7种：满减、折扣、无门槛、加购、品类、新人、限时

### Q-003
[Question]
用户登录系统方式？

[Answer]
用户名+密码，注册界面有角色选择（管理员、运营人员、核销人员、普通用户）

### Q-004
[Question]
AI模型选择？

[Answer]
参考bedrock.service.ts，支持SDK/API Key双模式，运行时选模型

### Q-005
[Question]
部署方式？

[Answer]
本地运行演示，通过登录不同账户模拟不同角色

### Q-006
[Question]
前端UI风格？

[Answer]
美观实用，简洁大方

### Q-007
[Question]
核销方式？

[Answer]
输入券码+点击核销按钮

### Q-008
[Question]
通知方式？

[Answer]
纯站内通知（铃铛+未读数+消息列表）

## 决策与变更记录

| 日期 | 决策 | 原因 |
|------|------|------|
| 2026-07-29 | 技术栈选Next.js全栈+SQLite | 单机部署最简单，与skill技术方向一致 |
| 2026-07-29 | 优惠券金额/类型可自选有默认值 | 用户补充需求 |
| 2026-07-29 | 安全/审计方向扩展不加 | 用户决定功能范围够了 |
