# 🐛 移动端问题日志

> 记录开发过程中遇到的所有问题、原因、解决方案

---

## ISSUE-001: verifier.py /records 路由渲染了错误的模板

- **日期**: 2026-07-30 (代码审计发现)
- **状态**: ✅ 已修复
- **发现方式**: 代码审计
- **问题**: `@verifier_bp.route('/records')` 中 `render_template('verifier/index.html')` 渲染了核销首页，而不是核销记录页
- **根因**: 创建路由时复制了 index.html 的模板路径，忘记修改为 records.html
- **影响**: 导航到"核销记录"时看到的是核销首页
- **修复**: 改为 `render_template('verifier/records.html')`
- **关联**: M-003

---

## ISSUE-002: app.py 未绑定 0.0.0.0

- **日期**: 2026-07-30 (代码审计发现)
- **状态**: ✅ 已修复
- **发现方式**: 代码审计
- **问题**: `app.run(debug=True, port=5000)` 只绑定 localhost，手机无法通过 IP 访问
- **根因**: Flask 默认只监听 127.0.0.1
- **影响**: 手机扫码后无法打开网页
- **修复**: 改为 `app.run(host='0.0.0.0', debug=True, port=5000)`
- **关联**: ADR-M-005

---

## ISSUE-003: （预期）跨域访问问题

- **日期**: —
- **状态**: ⚠️ 待验证
- **问题**: 手机通过 IP 访问时，如果 API 请求使用域名可能会失败
- **解决方案**:
  - 使用 `window.location.origin` 动态获取当前主机地址
  - 所有 API 请求使用相对路径 `/api/...`

---

## ISSUE-004: scan.py 需要单独 Blueprint 而非在 verifier.py 中

- **日期**: 2026-07-30 (实现时发现)
- **状态**: ✅ 已解决
- **发现方式**: 实现时发现
- **问题**: 扫码落地页 `/v/<coupon_code>` 需要短路径，但 verifier blueprint 注册在 `/verifier` 前缀下，导致 URL 变成 `/verifier/v/CPN-XXXX`
- **根因**: Blueprint URL 前缀自动拼接
- **解决方案**: 创建独立的 `routes/scan.py` 蓝图，无 URL 前缀，注册在 `scan_bp` 直接绑定 `/v/`
- **影响**: 二维码 URL 保持预期格式 `/v/CPN-XXXX`

---

## ISSUE-005: （已解决）核销记录页面不需要单独的 API

- **日期**: 2026-07-30 (实现时确认)
- **状态**: ✅ 已解决
- **问题**: 怀疑是否需要新建 API 端点来支持 records.html 的分页和统计
- **解决方案**: 通过检查发现 `GET /api/redeem/records` 已存在且返回完整列表（含 `redeemed_at`, `coupon_code`, `campaign_name`, `verifier_name`），前端通过 Alpine.js 实现本地分页、搜索和统计，不需要新增 API

---

## ISSUE-006: 二维码重复生成

- **日期**: 2026-07-30 (测试时发现)
- **状态**: ✅ 已修复
- **发现方式**: 用户反馈
- **问题**: 优惠券详情页生成了两个相同的二维码
- **根因**: Alpine.js 的 `x-init` 在组件初始化时触发了两次 `$nextTick` 回调，导致 `new QRCode()` 被调用了两次。qrcodejs 库默认在容器内追加 canvas/img，不会清空已有内容
- **影响**: 页面上显示两个完全相同的二维码，影响视觉效果
- **修复**: 在 `new QRCode()` 之前加入 `qrContainer.innerHTML = ''`，确保容器每次都被清空

---

## ISSUE-007: 扫码登录后 session 未传导到页面跳转

- **日期**: 2026-07-30 (测试时发现)
- **状态**: ✅ 已修复（2026-07-30 修订方案）
- **发现方式**: 用户反馈（手机端扫码后登录，显示核销失败，但后台显示核销成功）
- **问题**: scan_login.html 登录后跳转到 `/v/CPN-XXXX` 进行自动核销，但 session cookie 在跳转后丢失，导致扫码落地页认为用户未登录，渲染的 scan_result.html 无法正常核销
- **根因** (第一轮修复): 原流程（第一轮）在 scan_login.html 中 fetch 登录后 `window.location.href` 跳转到 `/v/CPN-XXXX`，浏览器导航时 cookie 可能未完全写入，移动浏览器 cookie 处理存在时序问题
- **根因** (第二轮修复): 即使 cookie 写入完成，`/v/CPN-XXXX` 页面上的 `scan_result.html` 的 `autoRedeem()` 也依赖 session cookie 来鉴权，但 `fetch('/api/redeem')` 是同一个页面内的请求，应该能携带 cookie。最终修复改为：登录 + 核销都在同一页面完成（两步 fetch），核销成功后再跳转到 `/verifier` 首页
- **影响**: 用户体验断档：扫码 → 登录 → 显示"核销失败 ❌" → 但实际上后端已成功核销
- **修复** (第一轮, 2026-07-30): 改为登录成功后 `window.location.href = '/v/' + couponCode` 跳转到扫码落地页自动核销 → **不完整**
- **修复** (最终, 2026-07-30): 登录成功后在同一页面直接调用 `/api/redeem` 核销 API，显示结果后跳转到 `/verifier` 首页。消除了 cookie 时序依赖

- **日期**: 2026-07-30 (实现时确认)
- **状态**: ✅ 已解决
- **问题**: 怀疑是否需要新建 API 端点来支持 records.html 的分页和统计
- **解决方案**: 通过检查发现 `GET /api/redeem/records` 已存在且返回完整列表（含 `redeemed_at`, `coupon_code`, `campaign_name`, `verifier_name`），前端通过 Alpine.js 实现本地分页、搜索和统计，不需要新增 API

---

## ISSUE-004: （预期）PWA 需要 HTTPS

- **日期**: —
- **状态**: ⚠️ 待验证
- **问题**: PWA 的 `beforeinstallprompt` 事件在 HTTP 下不会触发（localhost 除外）
- **解决方案**:
  - 演示时使用 localhost 访问
  - 如果部署到服务器，需配置 HTTPS
  - 没有 HTTPS 不影响核心功能（扫码核销），只影响"添加到主屏幕"
