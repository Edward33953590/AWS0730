# API 接口设计

## 全局约定

- **Base URL**：`http://localhost:3000/api`
- **认证方式**：JWT Bearer Token（Header: `Authorization: Bearer <token>`）
- **请求格式**：JSON（Content-Type: application/json）
- **响应格式**：

```json
// 成功
{ "success": true, "data": { ... } }

// 失败
{ "success": false, "error": { "code": "ERROR_CODE", "message": "错误描述" } }
```

- **分页格式**（列表接口）：

```json
{
  "success": true,
  "data": { "items": [...], "total": 100, "page": 1, "pageSize": 20 }
}
```

- **错误码约定**：

| HTTP状态码 | 含义 |
|-----------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 冲突（如重复领取） |
| 429 | 频率限制 |
| 500 | 服务器内部错误 |

---

## 1. 认证接口

### POST /api/auth/register
**权限**：公开

**请求体**：
```json
{
  "username": "string (3-20字符)",
  "password": "string (6-50字符)",
  "role": "ADMIN | OPERATOR | VERIFIER | USER"
}
```

**成功响应**：
```json
{
  "success": true,
  "data": {
    "user": { "id": "cuid", "username": "xxx", "role": "USER" },
    "token": "jwt_token"
  }
}
```

**错误**：
- 409: `{ "code": "USERNAME_EXISTS", "message": "用户名已被占用" }`

---

### POST /api/auth/login
**权限**：公开

**请求体**：
```json
{
  "username": "string",
  "password": "string"
}
```

**成功响应**：同注册

**错误**：
- 401: `{ "code": "INVALID_CREDENTIALS", "message": "用户名或密码错误" }`

---

### GET /api/auth/me
**权限**：已登录

**成功响应**：
```json
{
  "success": true,
  "data": { "id": "cuid", "username": "xxx", "role": "OPERATOR", "createdAt": "..." }
}
```

---

## 2. 活动管理接口

### GET /api/campaigns
**权限**：所有已登录用户
**查询参数**：`?page=1&pageSize=20&type=DISCOUNT&status=active`

**响应data.items**：
```json
{
  "id": "cuid",
  "name": "满100减20",
  "type": "FULL_REDUCTION",
  "params": { "threshold": 100, "discount": 20 },
  "totalStock": 100,
  "remainingStock": 85,
  "limitPerUser": 1,
  "validityMode": "RELATIVE",
  "validityDays": 1,
  "startTime": "2026-07-29T00:00:00Z",
  "transferable": true,
  "stackable": false,
  "shareable": true,
  "shareLimit": 3,
  "createdBy": "operator_user_id",
  "createdAt": "..."
}
```

---

### GET /api/campaigns/:id
**权限**：所有已登录用户

---

### POST /api/campaigns
**权限**：运营人员

**请求体**：
```json
{
  "name": "夏日满减活动",
  "description": "夏日清凉大促",
  "type": "FULL_REDUCTION",
  "params": { "threshold": 100, "discount": 20 },
  "totalStock": 100,
  "limitPerUser": 1,
  "validityMode": "RELATIVE",
  "validityDays": 1,
  "startTime": "2026-07-29T10:00:00Z",
  "transferable": false,
  "stackable": false,
  "shareable": true,
  "shareLimit": 3,
  "templateId": "optional_template_id"
}
```

---

### PUT /api/campaigns/:id
**权限**：运营人员
**注意**：库存只能增加，不可减少到低于已发放数

---

### DELETE /api/campaigns/:id
**权限**：运营人员
**注意**：已有领取记录的活动不可删除（软删除或拒绝）

---

### POST /api/campaigns/batch-send
**权限**：运营人员

**请求体**：
```json
{
  "campaignId": "cuid",
  "userIds": ["uid1", "uid2", "uid3"]
}
```

**响应**：
```json
{
  "success": true,
  "data": { "sent": 3, "skipped": 0, "details": [...] }
}
```

---

## 3. 优惠券接口

### POST /api/coupons/claim
**权限**：普通用户

**请求体**：
```json
{ "campaignId": "cuid" }
```

**成功响应**：
```json
{
  "success": true,
  "data": {
    "couponId": "cuid",
    "couponCode": "CPN-A3X9K2M7",
    "expiresAt": "2026-07-30T16:00:00Z",
    "recommendation": {
      "reason": "AI推荐理由文本（如果有）"
    }
  }
}
```

**错误**：
- 409: `ALREADY_CLAIMED` / `OUT_OF_STOCK` / `CAMPAIGN_NOT_STARTED` / `CAMPAIGN_ENDED`
- 403: `RISK_BLOCKED`（风控拦截）

---

### GET /api/coupons/my
**权限**：普通用户
**查询参数**：`?status=CLAIMED&page=1&pageSize=20`

---

### POST /api/coupons/transfer
**权限**：普通用户

**请求体**：
```json
{
  "couponId": "cuid",
  "targetUsername": "friend_user"
}
```

---

### POST /api/coupons/share
**权限**：普通用户

**请求体**：
```json
{ "campaignId": "cuid" }
```

**响应**：
```json
{
  "success": true,
  "data": { "shareCode": "abc123", "shareUrl": "/share/abc123", "maxClaims": 3 }
}
```

---

### POST /api/coupons/claim-share/:code
**权限**：普通用户

---

### GET /api/coupons/ranking
**权限**：所有已登录用户
**响应**：TOP 10 热门优惠券活动列表

---

## 4. 核销接口

### POST /api/redeem
**权限**：核销人员

**请求体**：
```json
{ "couponCode": "CPN-A3X9K2M7" }
```

**成功响应**：
```json
{
  "success": true,
  "data": {
    "status": "REDEEMED",
    "couponCode": "CPN-A3X9K2M7",
    "campaignName": "满100减20",
    "redeemedAt": "2026-07-29T16:30:00Z"
  }
}
```

**错误**：
- 404: `INVALID_CODE`（无效券码）
- 409: `ALREADY_REDEEMED`（已核销，返回首次核销信息）
- 410: `COUPON_EXPIRED`（已过期）

---

### GET /api/redeem/records
**权限**：核销人员
**查询参数**：`?page=1&pageSize=20`

---

## 5. AI接口

### POST /api/ai/recommend
**权限**：普通用户

**响应**：
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "campaignId": "cuid",
        "campaignName": "满100减20",
        "reason": "根据您近期的消费习惯，这张满减券可以帮您在日常购物中节省开支",
        "score": 0.95
      }
    ],
    "source": "ai" | "fallback"
  }
}
```

---

### POST /api/ai/risk-check
**权限**：系统内部调用（领券时自动触发）

**请求体**：
```json
{
  "userId": "cuid",
  "action": "CLAIM",
  "campaignId": "cuid",
  "metadata": { "requestCount": 5, "timeWindow": "10s" }
}
```

**响应**：
```json
{
  "score": 85,
  "decision": "BLOCK",
  "reason": "短时间内高频请求",
  "aiExplanation": "该用户在过去10秒内发起了52次领券请求...",
  "source": "ai" | "rule_engine"
}
```

---

### POST /api/ai/generate-copy
**权限**：运营人员

**请求体**：
```json
{
  "type": "FULL_REDUCTION",
  "params": { "threshold": 100, "discount": 20 },
  "context": "夏季促销"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "title": "清凉一夏 满100立减20",
    "description": "炎炎夏日，为您送上清凉优惠...",
    "slogan": "满百减二十，清凉不打折"
  }
}
```

---

### GET /api/ai/user-profile/:userId
**权限**：管理员

**响应**：
```json
{
  "success": true,
  "data": {
    "tags": ["价格敏感型", "高频用户", "食品品类偏好"],
    "summary": "该用户偏好满减类优惠券...",
    "source": "ai" | "rule_based"
  }
}
```

---

### GET /api/ai/models
**权限**：管理员

**响应**：可用的Bedrock模型列表

---

## 6. 统计与管理接口

### GET /api/stats/overview
**权限**：管理员

**响应**：
```json
{
  "success": true,
  "data": {
    "totalCampaigns": 15,
    "totalCoupons": 1200,
    "claimRate": 0.75,
    "redeemRate": 0.45,
    "totalUsers": 200,
    "riskBlocks": 12,
    "charts": {
      "dailyClaims": [...],
      "typeDistribution": [...],
      "redeemTrend": [...]
    }
  }
}
```

---

### GET /api/stats/export
**权限**：管理员
**查询参数**：`?format=csv|excel&type=claims|redemptions|campaigns&from=date&to=date`
**响应**：文件下载

---

### GET /api/logs
**权限**：管理员
**查询参数**：`?page=1&pageSize=50&action=CLAIM&userId=xxx&from=date&to=date`

---

### GET /api/notifications
**权限**：已登录用户
**查询参数**：`?page=1&pageSize=20&unreadOnly=true`

---

### PUT /api/notifications/:id/read
**权限**：已登录用户（只能操作自己的通知）

---

### PUT /api/notifications/read-all
**权限**：已登录用户

---

## 7. 黑白名单与收藏接口

### GET /api/blacklist
**权限**：运营人员
**查询参数**：`?type=BLACK|WHITE&page=1&pageSize=20`

### POST /api/blacklist
**权限**：运营人员
**请求体**：`{ "userId": "cuid", "type": "BLACK", "reason": "异常行为" }`

### DELETE /api/blacklist/:id
**权限**：运营人员

---

### GET /api/favorites
**权限**：普通用户

### POST /api/favorites
**权限**：普通用户
**请求体**：`{ "campaignId": "cuid" }`

### DELETE /api/favorites/:id
**权限**：普通用户

---

## 8. 模板接口

### GET /api/templates
**权限**：运营人员

### POST /api/templates
**权限**：运营人员
**请求体**：`{ "name": "满减模板", "config": { ... } }`

### DELETE /api/templates/:id
**权限**：运营人员
