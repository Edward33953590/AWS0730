# 📱 移动端扫码核销功能

## 概述

为优惠券发放与核销中心增加**手机扫码核销**能力，形成完整闭环：用户展示二维码 → 核销员扫码 → 自动核销。零输入、2秒完成。

## 目录结构

```
mobile/
├── README.md              ← 本文件（入口说明）
├── plan.md                ← 主计划（任务分解、进度追踪、中断恢复）
├── references/
│   ├── decisions.md       ← 决策日志（8个 ADR，记录每个技术选择及理由）
│   ├── issues.md          ← 问题日志（开发中遇到的问题和解决方案）
│   ├── architecture.md    ← 架构参考（路由/模板/API/依赖一览）
│   ├── test-cases.md      ← 测试用例（15条，可复用，含前置条件和预期）
│   └── test-run-2026-07-30.md  ← 测试执行记录（实际运行结果）
```

## 快速导航

| 你想做什么 | 看什么文件 |
|-----------|-----------|
| 了解功能范围 | `plan.md` — 任务清单和进度 |
| 了解技术决策 | `references/decisions.md` — 为什么选PWA不选原生App |
| 了解已修复的bug | `references/issues.md` — verifier.py模板渲染错误等 |
| 了解路由和API | `references/architecture.md` — 新增路由/模板一览 |
| 跑测试 | `references/test-cases.md` — 前置条件和步骤 |
| 查看测试结果 | `references/test-run-2026-07-30.md` — 实际运行输出 |

## 实现状态

| 任务 | 状态 | 说明 |
|------|------|------|
| M-001 用户端二维码 | ✅ 完成 | 优惠券详情页 + qrcode.js 生成二维码 |
| M-002 扫码落地页 | ✅ 完成 | 三路分支：已登录核销/未登录登录/权限不足 |
| M-003 核销记录页 | ✅ 完成 | 统计卡片 + 表格/卡片双布局 + 搜索分页 |
| M-004 PWA 支持 | ✅ 完成 | manifest.json + sw.js + 注册代码 |
| M-005 振动反馈 | ✅ 完成 | 3个核销页面均有振动反馈 |
| M-006 响应式适配 | ✅ 完成 | 移动端卡片布局 + 表格横向滚动 |
| M-007 分享功能 | ✅ 完成 | Web Share API + 降级复制剪贴板 |

## 核心文件影响

```
coupon-center/
├── app.py                          [修改] host='0.0.0.0', 注册 scan_bp
├── routes/scan.py                  [新增] /v/<code> 扫码落地页蓝图
├── routes/user.py                  [修改] /user/coupons/<id> 详情页
├── routes/verifier.py              [修改] /records 修复 records.html
├── templates/user/coupon_detail.html [新增] 详情页+QR码
├── templates/verifier/scan_result.html [新增] 扫码结果页
├── templates/verifier/scan_login.html  [新增] 扫码登录页
├── templates/verifier/records.html     [新增] 核销记录页
├── templates/verifier/index.html   [修改] 振动反馈+横向滚动
├── templates/base.html             [修改] manifest+SW注册
├── static/manifest.json            [新增] PWA清单
└── static/sw.js                    [新增] Service Worker
```

## 演示流程

```
1. 用户登录 → 我的券包 → 某券"详情"
2. 手机展示二维码（内容: http://IP:5000/v/CPN-XXXX）
3. 核销员用手机相机扫码 → 点"打开"
4. 自动核销成功 → 振动反馈 ✅ （全程约2秒）
```

## 中断恢复

如果实施中断，按以下步骤恢复：

1. 看 `plan.md` 了解当前进度
2. 看 `references/issues.md` 了解已知问题
3. 完成的任务不用重新做，直接继续下一个

---

> 创建时间：2026-07-30  
> 基于 `goal/mobile_plan.md` 实现，完整过程文档保存在本目录
