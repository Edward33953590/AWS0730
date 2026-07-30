# 🏗️ 移动端架构参考

> 移动端新增的路由、模板、API 关系图

---

## 路由表

| 方法 | 路径 | 用途 | 所属文件 | 新增/修改 |
|------|------|------|---------|-----------|
| GET | `/user/coupons/<coupon_id>` | 优惠券详情页（含二维码） | `routes/user.py` | 新增 |
| GET | `/v/<coupon_code>` | 扫码落地页 | `routes/verifier.py` | 新增 |
| GET | `/verifier/records` | 核销记录页 | `routes/verifier.py` | 修改 |

## 模板表

| 模板 | 用途 | 新增/修改 |
|------|------|-----------|
| `user/coupon_detail.html` | 优惠券详情 + QR 码 | 新增 |
| `verifier/scan_result.html` | 扫码落地 + 自动核销结果 | 新增 |
| `verifier/scan_login.html` | 扫码后未登录时的内嵌登录页 | 新增 |
| `verifier/records.html` | 核销记录列表 | 新增 |
| `base.html` | 添加 manifest 链接、导航链接 | 修改 |

## 静态文件

| 文件 | 用途 |
|------|------|
| `static/manifest.json` | PWA 清单 |
| `static/sw.js` | Service Worker |

## API 依赖（已有接口，不改）

| 方法 | 路径 | 用途 |
|------|------|------|
| POST | `/api/redeem` | 核销接口 |
| POST | `/api/auth/login` | 登录接口 |
| GET | `/api/redeem/records` | 核销记录 |
| GET | `/api/coupons/<id>` | 优惠券详情 |

## CDN 依赖

| 库 | 用途 | 加载方式 |
|----|------|---------|
| `qrcode.js` | 二维码生成 | CDN script |
| Alpine.js | 前端交互 | 已在 base.html |
| Chart.js | 图表 | 已在 base.html |
