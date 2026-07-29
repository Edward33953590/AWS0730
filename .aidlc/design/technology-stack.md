# 技术栈文档（修订版 - Python）

> 变更原因：Node.js环境安装失败，用户选择切换到Python技术栈

## 1. 核心技术栈

| 类别 | 技术 | 版本 | 选择理由 |
|------|------|------|----------|
| 语言 | Python | 3.11 | 用户环境已有 |
| Web框架 | Flask | 3.x | 轻量全栈，Jinja2模板渲染 |
| 模板引擎 | Jinja2 | 3.x | Flask内置 |
| 样式 | TailwindCSS | CDN | 无需Node构建 |
| 前端交互 | Alpine.js | CDN | 超轻量响应式JS框架 |
| 图表 | Chart.js | CDN | 轻量图表库 |
| 数据库 | SQLite | 3.x | Python内置支持 |
| ORM | SQLAlchemy + Flask-SQLAlchemy | 2.x | Python最流行ORM |
| 数据库迁移 | Flask-Migrate (Alembic) | 4.x | Schema版本管理 |
| 认证 | Flask-Login + JWT (PyJWT) | | 会话管理+API认证 |
| 密码 | Werkzeug (pbkdf2) | | Flask内置密码哈希 |
| AI | boto3 (Bedrock Runtime) | | AWS SDK for Python |
| 数据导出 | openpyxl | | Excel导出 |
| 表单 | Flask-WTF | | 表单校验+CSRF |

## 2. 完整依赖列表 (requirements.txt)

```
flask>=3.0.0
flask-sqlalchemy>=3.1.0
flask-migrate>=4.0.0
flask-login>=0.6.0
flask-wtf>=1.2.0
pyjwt>=2.8.0
boto3>=1.34.0
openpyxl>=3.1.0
python-dotenv>=1.0.0
```

## 3. 前端CDN依赖（无需安装）

```html
<!-- TailwindCSS -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- Alpine.js (轻量响应式交互) -->
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>

<!-- Chart.js (图表) -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- Lucide Icons -->
<script src="https://unpkg.com/lucide@latest"></script>
```

## 4. 项目结构

```
coupon-center/
├── app.py                  # Flask应用入口
├── config.py               # 配置文件
├── requirements.txt        # Python依赖
├── .env.example            # 环境变量模板
├── .env                    # 本地环境变量（不提交）
├── models/                 # 数据模型
│   ├── __init__.py
│   ├── user.py
│   ├── campaign.py
│   ├── coupon.py
│   ├── redemption.py
│   ├── notification.py
│   ├── risk_log.py
│   ├── operation_log.py
│   ├── share_link.py
│   ├── blacklist.py
│   ├── template.py
│   └── favorite.py
├── services/               # 业务逻辑层
│   ├── __init__.py
│   ├── auth_service.py
│   ├── campaign_service.py
│   ├── coupon_service.py
│   ├── redemption_service.py
│   ├── bedrock_service.py
│   ├── risk_engine.py
│   ├── stats_service.py
│   ├── notification_service.py
│   └── log_service.py
├── routes/                 # 路由/视图
│   ├── __init__.py
│   ├── auth.py
│   ├── user.py
│   ├── operator.py
│   ├── verifier.py
│   ├── admin.py
│   └── api.py             # JSON API接口
├── templates/              # Jinja2 HTML模板
│   ├── base.html           # 基础布局
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── user/
│   │   ├── index.html
│   │   ├── explore.html
│   │   ├── coupons.html
│   │   ├── favorites.html
│   │   ├── ranking.html
│   │   └── notifications.html
│   ├── operator/
│   │   ├── index.html
│   │   ├── campaigns.html
│   │   ├── create.html
│   │   ├── edit.html
│   │   ├── templates.html
│   │   ├── batch.html
│   │   └── blacklist.html
│   ├── verifier/
│   │   ├── index.html
│   │   └── records.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── logs.html
│   │   ├── export.html
│   │   ├── risk.html
│   │   └── profiles.html
│   └── share.html
├── static/                 # 静态资源
│   └── js/
│       └── app.js          # 通用JS工具函数
├── migrations/             # 数据库迁移（Flask-Migrate生成）
└── seed.py                 # 种子数据脚本
```

## 5. 启动命令

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
flask db upgrade
python seed.py

# 启动开发服务器
python app.py
# 或
flask run --debug --port 5000
```

## 6. 约束与替代方案

| 约束 | 当前选择 | 替代方案 | 不选择的原因 |
|------|----------|----------|-------------|
| 无Node环境 | Flask+Jinja2 | Django | Django过重，Flask更灵活 |
| 前端样式 | TailwindCSS CDN | Bootstrap | Tailwind更现代，CDN同样方便 |
| 前端交互 | Alpine.js CDN | jQuery/原生JS | Alpine.js声明式语法，与HTML集成好 |
| 图表 | Chart.js CDN | ECharts | Chart.js更轻量 |
| ORM | SQLAlchemy | Peewee | SQLAlchemy生态最大 |
