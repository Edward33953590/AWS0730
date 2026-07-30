# UI 元素 ID 接口说明（自动化测试用）

> 命名规则：`<页面功能>_<组件功能>_<组件类型>_<随机4位>`
> 
> 注意：修改 HTML 样式时**不得改动 id 属性**。

---

## 1. 登录页面 `/login`

| ID | 类型 | 功能说明 | 操作 |
|----|------|----------|------|
| `login_username_input_a1b2` | input[text] | 用户名输入框 | 输入用户名 |
| `login_password_input_c3d4` | input[password] | 密码输入框 | 输入密码 |
| `login_submit_button_e5f6` | button[submit] | 登录提交按钮 | 点击登录 |
| `login_demoadmin_button_g7h8` | button | 演示快速登录-管理员 | 点击自动填入admin账号并登录 |
| `login_demooperator_button_i9j0` | button | 演示快速登录-运营人员 | 点击自动填入operator账号并登录 |
| `login_demoverifier_button_k1l2` | button | 演示快速登录-核销人员 | 点击自动填入verifier账号并登录 |
| `login_demouser_button_m3n4` | button | 演示快速登录-普通用户 | 点击自动填入user1账号并登录 |

---

## 2. 注册页面 `/register`

| ID | 类型 | 功能说明 | 操作 |
|----|------|----------|------|
| `register_username_input_p5q6` | input[text] | 用户名输入框 | 输入用户名(3-20字符) |
| `register_password_input_r7s8` | input[password] | 密码输入框 | 输入密码(6-50字符) |
| `register_role_select_t9u0` | select | 角色选择下拉框 | 选择: USER/OPERATOR/VERIFIER/ADMIN |
| `register_submit_button_v1w2` | button[submit] | 注册提交按钮 | 点击注册 |

---

## 3. 核销页面 `/verifier`

| ID | 类型 | 功能说明 | 操作 |
|----|------|----------|------|
| `verifier_couponcode_input_x3y4` | input[text] | 券码输入框 | 输入券码(如CPN-A3X9K2M7) |
| `verifier_redeem_button_z5a6` | button | 核销按钮 | 点击核销 |

---

## 4. 运营-创建活动页面 `/operator/campaigns/create`

| ID | 类型 | 功能说明 | 操作 |
|----|------|----------|------|
| `create_name_input_b7c8` | input[text] | 活动名称输入框 | 输入活动名称 |
| `create_aicopy_button_d9e0` | button | AI文案生成按钮 | 点击生成AI营销文案 |
| `create_type_select_f1g2` | select | 优惠券类型选择 | 选择: FULL_REDUCTION/DISCOUNT/NO_THRESHOLD/ADD_ON/CATEGORY/NEWCOMER/TIME_LIMITED |
| `create_submit_button_h3i4` | button[submit] | 创建活动提交按钮 | 点击创建活动 |

---

## 3. 核销页面 `/verifier`

| ID | 类型 | 功能说明 | 操作 |
|----|------|----------|------|
| `verifier_couponcode_input_x3y4` | input[text] | 券码输入框 | 输入券码(如CPN-A3X9K2M7) |
| `verifier_redeem_button_z5a6` | button | 核销按钮 | 点击核销 |

---

## 4. 运营-创建活动页面 `/operator/campaigns/create`

| ID | 类型 | 功能说明 | 操作 |
|----|------|----------|------|
| `create_name_input_b7c8` | input[text] | 活动名称输入框 | 输入活动名称 |
| `create_aicopy_button_d9e0` | button | AI文案生成按钮 | 点击生成AI营销文案 |
| `create_type_select_f1g2` | select | 优惠券类型选择 | 选择: FULL_REDUCTION/DISCOUNT/NO_THRESHOLD/ADD_ON/CATEGORY/NEWCOMER/TIME_LIMITED |
| `create_submit_button_h3i4` | button[submit] | 创建活动提交按钮 | 点击创建活动 |

---

## 5. 全局组件 (base.html)

| ID | 类型 | 功能说明 | 操作 |
|----|------|----------|------|
| `base_notification_button_j2k3` | button | 顶栏通知铃铛按钮 | 点击展开通知 |

---

## 6. 管理员-数据导出 `/admin/export`

| ID | 类型 | 功能说明 | 操作 |
|----|------|----------|------|
| `export_claims_link_l4m5` | a[href] | 导出领券记录(CSV)链接 | 点击下载CSV文件 |

---

## 7. 分享领券页面 `/share/:code`

| ID | 类型 | 功能说明 | 操作 |
|----|------|----------|------|
| `share_claim_button_n6o7` | button | 分享链接领取按钮 | 点击领取优惠券 |
| `share_gotologin_link_p8q9` | a[href] | 未登录时跳转登录链接 | 点击跳转登录页 |

---

## 8. 用户-我的券包 `/user/coupons`

| ID | 类型 | 功能说明 | 操作 |
|----|------|----------|------|
| `coupons_filterall_button_r0s1` | button | 筛选-全部 | 显示所有券 |
| `coupons_filterclaimed_button_t2u3` | button | 筛选-待使用 | 只显示待使用的券 |
| `coupons_filterredeemed_button_v4w5` | button | 筛选-已核销 | 只显示已核销的券 |
| `coupons_filterexpired_button_x6y7` | button | 筛选-已过期 | 只显示已过期的券 |

---

## 9. 用户-通知页面 `/user/notifications`

| ID | 类型 | 功能说明 | 操作 |
|----|------|----------|------|
| `notifications_markallread_button_z8a9` | button | 全部已读按钮 | 将所有通知标为已读 |

---

## 10. 用户-首页 `/user`

| ID | 类型 | 功能说明 | 操作 |
|----|------|----------|------|
| `userhome_refresh_button_b1c2` | button | 刷新AI推荐按钮 | 重新加载AI推荐列表 |

---

## 11. 动态渲染组件（Alpine.js x-for 模板内）

以下组件通过 Alpine.js 动态渲染，无固定 ID，需通过选择器定位：

### 用户-浏览领券页面 `/user/explore`

| 选择器 | 功能说明 | 操作 |
|--------|----------|------|
| `button:contains('领取')` 或通过 campaign_id | 领取按钮 | 点击领取优惠券 |
| `.sidebar-link[href='/user/explore']` | 侧边栏-浏览领券 | 点击导航 |

### 用户-首页 `/user`

| 选择器 | 功能说明 | 操作 |
|--------|----------|------|
| `button:contains('刷新')` | 刷新AI推荐按钮 | 点击刷新推荐列表 |
| `button:contains('立即领取')` | 推荐券领取按钮 | 点击领取推荐的优惠券 |

### 用户-券包 `/user/coupons`

| 选择器 | 功能说明 | 操作 |
|--------|----------|------|
| `button:contains('出示券码')` | 出示券码按钮 | 点击显示券码(alert) |
| `button:contains('全部')` | 状态筛选-全部 | 切换显示全部券 |
| `button:contains('待使用')` | 状态筛选-待使用 | 切换显示待使用券 |

---

## 12. 侧边栏导航链接

| 选择器 | 角色 | 目标页面 |
|--------|------|----------|
| `a[href='/user']` | USER | 用户首页 |
| `a[href='/user/explore']` | USER | 浏览领券 |
| `a[href='/user/coupons']` | USER | 我的券包 |
| `a[href='/user/favorites']` | USER | 收藏夹 |
| `a[href='/user/ranking']` | USER | 排行榜 |
| `a[href='/user/notifications']` | USER | 通知 |
| `a[href='/operator']` | OPERATOR | 活动管理 |
| `a[href='/operator/campaigns/create']` | OPERATOR | 创建活动 |
| `a[href='/operator/templates']` | OPERATOR | 活动模板 |
| `a[href='/operator/batch']` | OPERATOR | 批量发券 |
| `a[href='/operator/blacklist']` | OPERATOR | 黑白名单 |
| `a[href='/verifier']` | VERIFIER | 核销操作 |
| `a[href='/verifier/records']` | VERIFIER | 核销记录 |
| `a[href='/admin']` | ADMIN | 统计面板 |
| `a[href='/admin/logs']` | ADMIN | 操作日志 |
| `a[href='/admin/risk']` | ADMIN | 风控监控 |
| `a[href='/admin/export']` | ADMIN | 数据导出 |
| `a[href='/admin/profiles']` | ADMIN | 用户画像 |
| `a[href='/logout']` | ALL | 退出登录 |

---

## 13. API 接口（配合自动化测试）

| 方法 | 路径 | 用途 | 请求体 |
|------|------|------|--------|
| POST | `/api/auth/login` | 登录 | `{"username":"xxx","password":"xxx"}` |
| POST | `/api/auth/register` | 注册 | `{"username":"xxx","password":"xxx","role":"USER"}` |
| GET | `/api/auth/me` | 当前用户 | - |
| POST | `/api/coupons/claim` | 领券 | `{"campaign_id":"xxx"}` |
| GET | `/api/coupons/my` | 我的券包 | - |
| POST | `/api/redeem` | 核销 | `{"coupon_code":"CPN-XXXXXXXX"}` |
| GET | `/api/redeem/records` | 核销记录 | - |
| GET | `/api/campaigns` | 活动列表 | - |
| POST | `/api/campaigns` | 创建活动 | `{"name":"xx","type":"FULL_REDUCTION","params":{},"total_stock":100}` |
| POST | `/api/ai/recommend` | AI推荐 | - |
| POST | `/api/ai/generate-copy` | AI文案 | `{"type":"FULL_REDUCTION","params":{"threshold":100,"discount":20}}` |
| POST | `/api/ai/risk-check` | 风控检测 | `{"action":"CLAIM"}` |
| GET | `/api/stats/overview` | 统计概览 | - |
| GET | `/api/stats/export?type=claims` | 数据导出 | - |
| GET | `/api/logs` | 操作日志 | - |
| GET | `/api/notifications` | 通知列表 | - |
| GET | `/api/notifications/unread-count` | 未读数 | - |
| GET | `/api/coupons/ranking` | 排行榜 | - |
| GET | `/api/favorites` | 收藏列表 | - |
| POST | `/api/favorites` | 添加收藏 | `{"campaign_id":"xxx"}` |
| GET | `/api/blacklist` | 黑白名单 | - |
| POST | `/api/blacklist` | 添加名单 | `{"username":"xx","type":"BLACK","reason":"xx"}` |

---

## 14. 自动化测试示例流程

```python
# 示例：Selenium 自动化演示流程
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get('http://localhost:5000/login')

# 1. 快速登录为运营人员
driver.find_element(By.ID, 'login_demooperator_button_i9j0').click()

# 2. 创建活动
driver.find_element(By.CSS_SELECTOR, "a[href='/operator/campaigns/create']").click()
name_input = driver.find_element(By.ID, 'create_name_input_b7c8')
name_input.clear()
name_input.send_keys('测试活动')
driver.find_element(By.ID, 'create_submit_button_h3i4').click()

# 3. 切换为普通用户
driver.get('http://localhost:5000/login')
driver.find_element(By.ID, 'login_demouser_button_m3n4').click()

# 4. 领取优惠券（通过API）
import requests
s = requests.Session()
s.post('http://localhost:5000/api/auth/login', json={'username':'user1','password':'user123'})
r = s.post('http://localhost:5000/api/coupons/claim', json={'campaign_id':'...'})
coupon_code = r.json()['data']['coupon_code']

# 5. 核销
driver.get('http://localhost:5000/login')
driver.find_element(By.ID, 'login_demoverifier_button_k1l2').click()
code_input = driver.find_element(By.ID, 'verifier_couponcode_input_x3y4')
code_input.send_keys(coupon_code)
driver.find_element(By.ID, 'verifier_redeem_button_z5a6').click()
```
