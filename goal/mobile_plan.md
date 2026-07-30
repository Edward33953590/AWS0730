# 📱 移动端增强计划 — 扫码核销

> 创建时间：2026-07-30  
> 项目：优惠券发放与核销中心  
> 目标：实现手机扫码核销闭环，提升竞赛演示冲击力  
> 预计总工时：8 小时  
> 依赖前置：无（独立于 P0 任务）

---

## 一、设计思路

### 核心痛点

当前核销需要手动输入 `CPN-XXXXXXXX` 券码，体验差、易输错、演示不酷。

### 解决方案：二维码扫码核销

```
用户手机上展示二维码 ──→ 核销员用手机相机扫码 ──→ 打开页面自动核销
                      ↑
                 二维码内容是完整 URL
```

**关键设计：核销员身份认证**

扫码后打开的页面需要确认核销员身份，设计了两级流程：

| 状态 | 行为 |
|------|------|
| 已登录且是核销员 | 直接自动核销 ✅ |
| 未登录 / session 过期 | 页面内嵌登录表单 → 登录成功 → 自动核销 |
| 已登录但不是核销员 | 提示"无核销权限"，引导切换账号 |

### 为什么不做原生 App

| 方案 | 工时 | 核销员操作 | 演示效果 |
|------|------|-----------|---------|
| ✅ **PWA + URL 扫码** | 8h | 相机扫 → 点弹窗 → 自动核销 | ⭐⭐⭐⭐⭐ |
| 微信小程序 | 40h+ | 需打开微信扫 | ⭐⭐⭐ |
| 原生 App | 80h+ | 需安装 | ⭐⭐⭐ |

---

## 二、完整用户流程

### 2.1 用户端：查看优惠券二维码

```
用户登录 → 我的券包 → 点击某张券 → 优惠券详情页（含二维码）
                                    ↓
                            二维码内容: https://host/v/CPN-A3F8K2M1
```

### 2.2 核销端：扫码核销（完整路径）

```
核销员用手机自带相机扫用户屏幕上的二维码
         │
         ▼ 相机识别出 URL
┌──────────────────────────────┐
│  🔗 打开此链接？             │
│  https://host/v/CPN-A3F8K2M1 │
│                              │
│  [打开]          [取消]       │
└──────────────────────────────┘
         │ 点"打开"
         ▼
┌──────────────────────────────────┐
│  检查登录状态                      │
│                                  │
├─ 已登录 + 核销员角色 ─→ 自动核销 ✅
│                                  │
├─ 已登录 + 非核销员 ─→ 提示权限不足
│                                  │
└─ 未登录 ──────────────────────┐
                                ▼
            ┌──────────────────────────────────┐
            │  核销员登录（内嵌在页面中）        │
            │                                  │
            │  券码: CPN-A3F8K2M1               │
            │  ─── 请登录核销员账号 ───         │
            │  [账号] ________________          │
            │  [密码] ________________          │
            │  [登录并核销]                      │
            │                                  │
            │  演示快速入口:                     │
            │  [verifier / verifier123]         │
            └──────────────────────────────────┘
                                │ 登录成功
                                ▼
                        ┌──────────────────┐
                        │  ✅ 核销成功！     │
                        │                   │
                        │  满100减50         │
                        │  CPN-A3F8K2M1     │
                        │  核销时间 10:32:15 │
                        │                   │
                        │  [继续核销]        │
                        └──────────────────┘
```

---

## 三、新增/修改文件清单

```
coupon-center/
├── templates/
│   ├── user/
│   │   └── coupon_detail.html     [新增] 优惠券详情 + 二维码
│   ├── verifier/
│   │   ├── scan_result.html       [新增] 扫码落地页 + 自动核销结果
│   │   ├── scan_login.html        [新增] 扫码后未登录时的内嵌登录页
│   │   └── records.html           [新增] 补齐核销记录页面
│   └── base.html                  [修改] 添加 PWA manifest 链接
├── routes/
│   ├── verifier.py                [修改] 加 v/<code> 扫码落地路由
│   └── api.py                     [修改] 调已有 redeem，无需新端点
└── static/
    ├── manifest.json              [新增] PWA 清单
    └── sw.js                      [新增] Service Worker
```

**后端已有的接口（不需要改）**：
- `POST /api/redeem` — 核销接口，已有

**需要新增的路由（2 个）**：
- `GET /v/<coupon_code>` — 扫码落地页（短路径，好输入）
- `GET /user/coupons/<coupon_id>` — 优惠券详情 + 二维码

---

## 四、任务分解与进度追踪

### 🔴 P0 — 核心功能（5 小时）

---

#### M-001: 用户端优惠券详情页 + 二维码

| 属性 | 内容 |
|------|------|
| **优先级** | 🔴 P0 |
| **预计工时** | 1.5 小时 |
| **状态** | ⏳ 未开始 |
| **依赖** | 无 |

**任务分解**：

- [ ] **001-1**: 创建 `templates/user/coupon_detail.html`
  - 显示优惠券信息：券码、活动名称、类型、状态、有效期
  - 大号 QR 码区域（使用 `qrcode.js` CDN）
  - 券码文字展示（二维码备选方案）
  - "分享"按钮
  - 状态：⏳ 未开始

- [ ] **001-2**: 添加用户路由 `GET /user/coupons/<coupon_id>`
  - 文件：`coupon-center/routes/user.py`
  - 查询 Coupon + Campaign 信息
  - 渲染 `coupon_detail.html`
  - 验证该优惠券属于当前用户
  - 状态：⏳ 未开始

- [ ] **001-3**: 在"我的券包"页面(`templates/user/coupons.html`)中，为每张优惠券添加"查看详情"按钮
  - 链接到 `/user/coupons/<coupon_id>`
  - 状态：⏳ 未开始

- [ ] **001-4**: 引入 qrcode.js CDN
  - 文件：`templates/base.html` 或 `coupon_detail.html`
  - `<script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>`
  - 状态：⏳ 未开始

- [ ] **001-5**: 实现前端二维码生成
  - JS 代码：根据券码生成 URL `https://host/v/{coupon_code}`
  - 调用 `new QRCode(element, {text: url, width: 200, height: 200})`
  - 状态：⏳ 未开始

- [ ] **001-6**: 测试验证
  - 访问 `/user/coupons` 能看到券列表
  - 点击券进入详情页，二维码正确显示
  - 用手机相机扫码，识别出正确 URL
  - 状态：⏳ 未开始

**验收标准**：
- [ ] 优惠券详情页展示券码、活动名称、状态、有效期
- [ ] 二维码正确编码 `https://host/v/CPN-XXXXXXXX` 格式的 URL
- [ ] 手机相机可扫码识别

**备注**：
```
二维码内容格式：https://当前域名/v/CPN-XXXXXXXX
当前域名从 window.location.origin 自动获取，不硬编码
```

---

#### M-002: 扫码落地页（核销 + 登录一体化）

| 属性 | 内容 |
|------|------|
| **优先级** | 🔴 P0 |
| **预计工时** | 2 小时 |
| **状态** | ⏳ 未开始 |
| **依赖** | 无（独立于 M-001） |

**任务分解**：

- [ ] **002-1**: 创建短路径路由 `GET /v/<coupon_code>`
  - 文件：`coupon-center/routes/verifier.py`
  - 判断 `current_user.is_authenticated` 和 `current_user.role == 'VERIFIER'`
  - 已登录 + 核销员 → 渲染 `scan_result.html`，传入 `coupon_code`
  - 未登录 → 渲染 `scan_login.html`，传入 `coupon_code`
  - 已登录但不是核销员 → 提示"需要核销员权限"
  - 状态：⏳ 未开始

```python
@verifier_bp.route('/v/<coupon_code>')
def scan_landing(coupon_code):
    """扫码落地页——核销员扫二维码后打开的页面"""
    code = coupon_code.strip().upper()
    if not current_user.is_authenticated:
        return render_template('verifier/scan_login.html', coupon_code=code)
    if current_user.role != 'VERIFIER':
        flash('需要核销员权限才能核销', 'error')
        return redirect('/')
    return render_template('verifier/scan_result.html', coupon_code=code)
```

- [ ] **002-2**: 创建扫码核销结果页 `templates/verifier/scan_result.html`
  - 页面加载后自动调用 `POST /api/redeem` 核销
  - 显示核销状态（成功/失败/已核销）
  - 成功时显示：优惠券名称、券码、核销时间
  - 失败时显示：错误信息、建议手动输入
  - 页面底部：继续核销按钮（回到核销首页）、手动输入按钮
  - 使用 Alpine.js 管理状态
  - 状态：⏳ 未开始

- [ ] **002-3**: 创建扫码登录页 `templates/verifier/scan_login.html`
  - 顶部显示券码 + 二维码状态
  - 核销员登录表单（账号 + 密码）
  - 登录成功后自动调用核销接口
  - ✅ 演示快速登录按钮（一键填入 `verifier / verifier123`）
  - 使用 Alpine.js 管理登录流程
  - 状态：⏳ 未开始

- [ ] **002-4**: 实现扫码登录页的前端逻辑
  - JS 函数：`loginAndRedeem()` — 调用 `POST /api/auth/login`
  - 登录成功后调用 `POST /api/redeem`
  - 显示结果（成功/失败）
  - 状态：⏳ 未开始

- [ ] **002-5**: 实现扫码核销结果页的前端逻辑
  - JS 函数：页面加载自动调 `POST /api/redeem`（带 `coupon_code`）
  - 处理响应：成功 ✅ / 已核销 ⚠️ / 失败 ❌
  - 每种状态显示不同样式和文案
  - 状态：⏳ 未开始

- [ ] **002-6**: 测试验证
  - 未登录时扫码 → 打开登录页 → 登录后自动核销
  - 已登录时扫码 → 直接显示核销结果
  - 重复扫码同一券码 → 显示"已核销"
  - 无效券码 → 显示"券码不存在"
  - 状态：⏳ 未开始

**验收标准**：
- [ ] 扫码落地页 `/v/CPN-XXX` 可访问
- [ ] 未登录时显示内嵌登录页，快速登录按钮可用
- [ ] 已登录核销员直接自动核销
- [ ] 核销结果正确显示（成功/已核销/失败）

**补充说明 — 扫码登录页的前端逻辑**：

```html
<!-- templates/verifier/scan_login.html 的核心 Alpine.js 逻辑 -->
<div x-data="{
    couponCode: '{{ coupon_code }}',
    username: '',
    password: '',
    loading: false,
    result: null,
    async quickLogin() {
        this.username = 'verifier';
        this.password = 'verifier123';
        await this.loginAndRedeem();
    },
    async loginAndRedeem() {
        this.loading = true;
        this.result = null;
        // 1. 登录
        const loginRes = await fetch('/api/auth/login', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: this.username, password: this.password})
        });
        const loginData = await loginRes.json();
        if (!loginData.success) {
            this.result = {type: 'error', msg: '登录失败: ' + loginData.error?.message};
            this.loading = false;
            return;
        }
        // 2. 核销
        const redeemRes = await fetch('/api/redeem', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({coupon_code: this.couponCode})
        });
        const redeemData = await redeemRes.json();
        if (redeemData.success) {
            this.result = {type: 'success', msg: '核销成功！', data: redeemData.data};
        } else {
            this.result = {type: 'error', msg: redeemData.error?.message || '核销失败'};
        }
        this.loading = false;
    }
}">
    <!-- 登录表单 + 核销结果显示 -->
</div>
```

**备注**：
```
二维码的 URL 路径用 /v/ 而不是 /verifier/ ：
- 更短，二维码更密集，易于扫码识别
- 评委看到 URL 更简洁美观
```

---

#### M-003: 补齐核销记录页面

| 属性 | 内容 |
|------|------|
| **优先级** | 🔴 P0 |
| **预计工时** | 1 小时 |
| **状态** | ⏳ 未开始 |
| **依赖** | 无 |

**任务分解**：

- [ ] **003-1**: 创建 `templates/verifier/records.html`
  - 调用 `GET /api/redeem/records` 获取核销记录列表
  - 显示表格：核销时间、券码、活动名称、核销员
  - 移动端适配（卡片式布局替代表格）
  - 搜索/筛选功能（可选，按券码搜索）
  - 分页功能
  - 空状态："暂无核销记录"
  - 状态：⏳ 未开始

- [ ] **003-2**: 在 `routes/verifier.py` 添加路由
  - `@verifier_bp.route('/records')` 指向 `records.html`
  - 状态：⏳ 未开始

- [ ] **003-3**: 将核销记录链接加入导航栏
  - 文件：`templates/base.html`
  - 在 verifier 的导航中加入"核销记录"
  - 状态：⏳ 未开始

- [ ] **003-4**: 测试验证
  - 页面显示正常
  - 有核销记录时列表展示
  - 无记录时显示空状态
  - 手机屏幕布局正常
  - 状态：⏳ 未开始

**验收标准**：
- [ ] `/verifier/records` 页面可访问
- [ ] 核销记录列表显示完整
- [ ] 移动端显示正常

---

### 🟡 P1 — 增强体验（3 小时）

---

#### M-004: PWA 支持（manifest + Service Worker）

| 属性 | 内容 |
|------|------|
| **优先级** | 🟡 P1 |
| **预计工时** | 1.5 小时 |
| **状态** | ⏳ 未开始 |
| **依赖** | 无 |

**任务分解**：

- [ ] **004-1**: 创建 `static/manifest.json`
  - name: "优惠券中心"
  - short_name: "券中心"
  - start_url: "/"
  - display: "standalone"（沉浸式，无浏览器地址栏）
  - icons: 48x48, 72x72, 96x96, 144x144, 192x192（使用内联 SVG 或 emoji 图标）
  - theme_color: "#3b82f6"（Tailwind primary blue）
  - background_color: "#f9fafb"（Tailwind gray-50）
  - 状态：⏳ 未开始

- [ ] **004-2**: 在 `templates/base.html` 中链接 manifest
  - `<link rel="manifest" href="/static/manifest.json">`
  - `<meta name="theme-color" content="#3b82f6">`
  - 状态：⏳ 未开始

- [ ] **004-3**: 创建 `static/sw.js` Service Worker
  - 缓存核心页面（首页、券包、核销等）
  - 离线时显示基本界面
  - 状态：⏳ 未开始

- [ ] **004-4**: 在 `templates/base.html` 注册 Service Worker
  - `navigator.serviceWorker.register('/static/sw.js')`
  - 状态：⏳ 未开始

- [ ] **004-5**: 测试验证
  - Chrome DevTools → Application → Manifest 显示正常
  - 手机浏览器可"添加到主屏幕"
  - 安装后打开无地址栏
  - 状态：⏳ 未开始

**验收标准**：
- [ ] manifest.json 配置正确
- [ ] 浏览器检测到 PWA 并提示安装
- [ ] 安装后以 standalone 模式打开

**备注**：
```
PWA 需要 HTTPS 才能安装。本地 localhost 也支持。
如果部署到服务器必须配置 HTTPS。
```

---

#### M-005: 扫码核销成功反馈增强

| 属性 | 内容 |
|------|------|
| **优先级** | 🟡 P1 |
| **预计工时** | 0.5 小时 |
| **状态** | ⏳ 未开始 |
| **依赖** | M-002 |

**任务分解**：

- [ ] **005-1**: 核销成功时添加振动反馈
  - `navigator.vibrate(200)` — 手机振动 200ms
  - 捕获 `vibrate` 不支持的异常（桌面浏览器无此 API）
  - 状态：⏳ 未开始

- [ ] **005-2**: 核销成功时播放提示音（可选）
  - 使用 Web Audio API 生成短促"叮"声
  - 或使用 Audio 标签播放预录音频
  - 状态：⏳ 未开始

- [ ] **005-3**: 测试验证
  - 手机扫码核销成功后振动
  - 桌面浏览器不报错
  - 状态：⏳ 未开始

**验收标准**：
- [ ] 手机核销成功时有振动反馈
- [ ] 桌面浏览器不报错

---

#### M-006: 响应式适配与细节优化

| 属性 | 内容 |
|------|------|
| **优先级** | 🟡 P1 |
| **预计工时** | 1 小时 |
| **状态** | ⏳ 未开始 |
| **依赖** | 无 |

**任务分解**：

- [ ] **006-1**: 检查核销相关页面在手机上的显示
  - 扫描 `templates/verifier/` 下所有页面
  - 确保 TailwindCSS 响应式类（`sm:`, `md:`）正确使用
  - 状态：⏳ 未开始

- [ ] **006-2**: 优化 "我的券包" 页面移动端卡片布局
  - 手机上使用卡片式布局替代表格
  - 加大触控区域（按钮至少 44px 高度）
  - 状态：⏳ 未开始

- [ ] **006-3**: 测试验证
  - 用 Chrome DevTools 模拟不同尺寸手机
  - 用实际手机打开测试
  - 状态：⏳ 未开始

**验收标准**：
- [ ] 核销相关页面在 375px~414px 宽度下布局正常
- [ ] 按钮和链接有足够的触控区域

---

### 🟢 P2 — 加分项（可选）

---

#### M-007: 核销分享功能

| 属性 | 内容 |
|------|------|
| **优先级** | 🟢 P2 |
| **预计工时** | 0.5 小时 |
| **状态** | ⏳ 未开始 |
| **依赖** | M-001 |

**任务分解**：

- [ ] **007-1**: 在优惠券详情页添加"分享"按钮
  - 使用 Web Share API: `navigator.share()`
  - 分享内容：券码、活动名称、核销链接
  - 降级方案：不支持 Web Share 时复制到剪贴板
  - 状态：⏳ 未开始

**验收标准**：
- [ ] 手机端点击分享可调用系统分享菜单
- [ ] 桌面端降级为复制链接

---

## 五、整体进度追踪

### 完成统计

| 状态 | 任务数 | 百分比 |
|------|--------|--------|
| ✅ 已完成 | 0/7 | 0% |
| 🔄 进行中 | 0/7 | 0% |
| ⏳ 未开始 | 7/7 | 100% |

### 进度一览

```
M-001 [          ] 0%  用户端二维码
M-002 [          ] 0%  扫码落地页
M-003 [          ] 0%  核销记录页面
M-004 [          ] 0%  PWA 支持
M-005 [          ] 0%  振动反馈
M-006 [          ] 0%  响应式适配
M-007 [          ] 0%  分享功能
```

---

## 六、中断恢复指南

如果实施中断，按以下步骤恢复：

1. **打开本计划文档** `goal/mobile_plan.md`
2. **搜索状态为 "🔄 进行中" 的子任务**
3. **从该子任务继续工作**
4. **完成后更新状态为 ✅**

### 快速查看进度

```bash
grep -E "^\-\ \[.\]|^\|.*M-\d|状态.*⏳|状态.*🔄" goal/mobile_plan.md
```

### 当前任务状态速查

| 任务 | 状态 | 最后操作 |
|------|------|---------|
| M-001 用户端二维码 | ⏳ 未开始 | - |
| M-002 扫码落地页 | ⏳ 未开始 | - |
| M-003 核销记录 | ⏳ 未开始 | - |
| M-004 PWA 支持 | ⏳ 未开始 | - |
| M-005 振动反馈 | ⏳ 未开始 | - |
| M-006 响应式适配 | ⏳ 未开始 | - |
| M-007 分享功能 | ⏳ 未开始 | - |

---

## 七、演示话术（30 秒）

```
[用户打开手机，展示优惠券二维码]
→ "每张优惠券都有专属二维码"

[核销员用手机自带相机扫码]
→ "核销员用任意手机相机扫码即可"

[弹窗点"打开"，自动核销成功]
→ "无需登录、无需输入任何文字，2 秒完成核销"
→ "如果核销员尚未登录，页面会引导一键登录后自动核销"
```

---

## 八、与现有计划的衔接

此计划独立于 `plan_v2.md` 的 P0/P1 任务。建议执行顺序：

1. 先完成 `plan_v2.md` 的 P0 任务（大屏、团队墙、反思文档、bug 修复）
2. 再开始本计划的 **M-001 + M-002**（3.5 小时，核心扫码流程）
3. 有时间继续 **M-003 + M-004**（2.5 小时，记录 + PWA）
4. 最后 **M-005 ~ M-007**（2 小时，锦上添花）

---

**文档结束**
