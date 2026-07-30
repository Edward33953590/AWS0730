# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A coupon issuance and redemption center built for the SRCG Workshop competition. The system supports 4 roles (ADMIN, OPERATOR, VERIFIER, USER) and 7 coupon types, with AI-powered features (recommendations, risk detection, copywriting, user profiling) via Amazon Bedrock.

**Stack:** Flask 3.x + SQLAlchemy + SQLite + Jinja2 + TailwindCSS (CDN) + Alpine.js 3.x + Chart.js + Lucide icons

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
cd coupon-center && python app.py
# Starts on http://localhost:5000

# Initialize/seed database
cd coupon-center && python seed.py

# Run frontend rendering tests
cd coupon-center && python test_frontend.py

# Test AI connectivity
cd coupon-center && python test_ai_call.py

# Debug authentication issues
cd coupon-center && python debug_login.py
```

## Architecture

### Directory Layout

```
coupon-center/
├── app.py            # Flask application factory, blueprint registration
├── config.py         # Configuration from environment variables
├── extensions.py     # Flask extensions (db, migrate, login, csrf)
├── seed.py           # Database seeder with demo data
├── .env              # Environment variables (committed — rotate sensitive values)
├── models/           # SQLAlchemy ORM models (11 models, one file each)
├── routes/           # Flask blueprints (7 route files)
│   ├── auth.py       # Login/register page routes (blueprint at "/")
│   ├── api.py        # All JSON API endpoints (blueprint at "/api")
│   ├── user.py       # User page routes ("/user")
│   ├── operator.py   # Operator page routes ("/operator")
│   ├── verifier.py   # Verifier page routes ("/verifier")
│   ├── admin.py      # Admin page routes ("/admin")
│   └── share.py      # Public share link page ("/share")
├── services/         # Business logic layer (14 services)
├── templates/        # Jinja2 HTML templates (role-based subdirectories)
└── instance/         # SQLite database file (coupon_center.db)
```

### Layered Architecture

**Routes** handle HTTP — they validate input, call services, and return responses. Page routes render Jinja2 templates; API routes return JSON.

**Services** contain business logic and are stateless (no class instances). Key services:
- `campaign_service.py` — Campaign CRUD with type-specific defaults (7 coupon types)
- `coupon_service.py` — Coupon claiming with atomic stock decrement via raw SQL
- `redemption_service.py` — Idempotent redemption (one coupon → one redemption)
- `risk_engine.py` — Rule-based fraud detection fallback (6 rules) and AI risk check
- `bedrock_service.py` — Amazon Bedrock Converse API (SDK mode + Bearer Token mode)
- `ai_recommend_service.py` — Personalized recommendations with popularity-based fallback
- `ai_copy_service.py` — AI copywriting with template-based fallback
- `ai_profile_service.py` — AI user profiling with rule-based fallback
- `stats_service.py` — Admin dashboard aggregate statistics
- `log_service.py` / `notification_service.py` / `share_service.py` — Supporting services

**Models** are SQLAlchemy ORM classes in `models/`, one file per model. All use `String(36)` UUID primary keys.

### AI Architecture

All AI services follow a **try/fallback** pattern:
1. Try Bedrock Converse API via `bedrock_service.py`
2. On failure, fall back to deterministic logic (popular coupons, rule engine, templates)

`bedrock_service.py` supports two auth modes:
- **SDK mode** (default): `boto3.client('bedrock-runtime')` with `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`
- **Bearer Token mode**: HTTP POST with `Authorization: Bearer <token>` (currently active in `.env`)

### Database (Schema Design)

11 tables. All IDs are UUID strings. Coupons have a unique `coupon_code` (format `CPN-XXXXXXXX`). The coupon claim logic uses **atomic stock decrement** (`UPDATE campaigns SET remaining_stock = remaining_stock - 1 WHERE ...`) to prevent overselling. Redemption is idempotent — one coupon can only be redeemed once.

**Coupon Status Flow:**
```
CLAIMED → REDEEMED
       → TRANSFERRED
       → EXPIRED
```

### 7 Coupon Types

| Type | Behavior |
|------|----------|
| FULL_REDUCTION | Spend X get Y off |
| DISCOUNT | Percentage off |
| NO_THRESHOLD | Fixed amount off, no minimum |
| ADD_ON | Buy X get free item |
| CATEGORY | Discount in specific category |
| NEWCOMER | First-time user only |
| TIME_LIMITED | Urgent flash sale window |

### Key Patterns

- **API routes** (`routes/api.py`) are CSRF-exempt via `csrf.exempt()` decorator
- **Page routes** use Flask-Login `login_required` + custom role decorators from `auth_service.py`
- **Alpine.js** is used for interactive UI (notification bell, coupon claiming, modals) via `x-data`, `x-on`, `x-show`
- **TailwindCSS** is configured via CDN with inline `<script>` config in `templates/base.html`
- **Templates** extend `base.html` which provides role-based nav, flash messages, and notification bell
