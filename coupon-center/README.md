# 优惠券发放与核销中心

SRCG Workshop 竞赛项目 - 基于 Flask + SQLite + Amazon Bedrock AI 的优惠券管理系统。

## 快速启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库 + 种子数据
python seed.py

# 3. 启动应用
python app.py
```

浏览器打开 http://localhost:5000

## 测试账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| operator | operator123 | 运营人员 |
| verifier | verifier123 | 核销人员 |
| user1 | user123 | 普通用户 |
| user2 | user123 | 普通用户 |
| user3 | user123 | 普通用户 |

## 竞赛演示流程

1. 运营（operator）登录 → 创建库存1的活动 → 点击AI生成文案
2. 用户1（user1）登录 → 领取该活动 → 成功（查看AI推荐）
3. 用户2（user2）登录 → 领取同一活动 → 失败（库存不足）
4. 核销人员（verifier）登录 → 输入券码 → 核销成功
5. 核销人员再次输入同一券码 → 返回"已核销"（幂等）
6. 用户3（user3）快速连续领券 → 触发风控拦截
7. 管理员（admin）登录 → 查看统计面板/图表
8. 管理员 → 查看操作日志
9. 管理员 → 导出数据CSV

## 技术栈

- **后端**: Flask 3.x + SQLAlchemy + SQLite
- **前端**: Jinja2 + TailwindCSS (CDN) + Alpine.js (CDN) + Chart.js (CDN)
- **AI**: Amazon Bedrock Converse API (boto3)
- **认证**: Flask-Login + Session

## 核心功能

- ✅ 4种角色（管理员/运营/核销/用户）
- ✅ 7种优惠券类型（满减/折扣/无门槛/加购/品类/新人/限时）
- ✅ 库存原子扣减（并发安全）
- ✅ 幂等核销
- ✅ AI智能推券（降级热门券）
- ✅ AI风控引擎（降级规则引擎）
- ✅ AI文案生成（降级预设模板）
- ✅ AI用户画像
- ✅ 通知系统（站内铃铛）
- ✅ 优惠券转赠/分享
- ✅ 收藏夹/排行榜
- ✅ 黑白名单管理
- ✅ 操作日志审计
- ✅ 数据统计+可视化图表
- ✅ 数据导出CSV

## AWS Bedrock 配置

在 `.env` 文件中配置 AWS 凭证：

```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
DEFAULT_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

> 不配置AWS凭证时，所有AI功能会自动降级为规则引擎/模板方案，系统仍可正常运行。
