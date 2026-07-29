"""Seed script - populate database with test data."""
import uuid
import json
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models.user import User
from models.campaign import Campaign


def seed():
    """Create test users and sample campaigns."""
    app = create_app()
    with app.app_context():
        # Check if already seeded
        if User.query.first():
            print("Database already has data. Skipping seed.")
            return

        print("Seeding database...")

        # Create test users (one for each role)
        users = [
            {'username': 'admin', 'password': 'admin123', 'role': 'ADMIN'},
            {'username': 'operator', 'password': 'operator123', 'role': 'OPERATOR'},
            {'username': 'verifier', 'password': 'verifier123', 'role': 'VERIFIER'},
            {'username': 'user1', 'password': 'user123', 'role': 'USER'},
            {'username': 'user2', 'password': 'user123', 'role': 'USER'},
            {'username': 'user3', 'password': 'user123', 'role': 'USER'},
        ]

        created_users = {}
        for u in users:
            user = User(id=str(uuid.uuid4()), username=u['username'], role=u['role'])
            user.set_password(u['password'])
            db.session.add(user)
            created_users[u['username']] = user
            print(f"  Created user: {u['username']} ({u['role']})")

        db.session.flush()

        # Create sample campaigns
        operator_id = created_users['operator'].id
        campaigns = [
            {
                'name': '夏日满减活动',
                'description': '夏日清凉大促，满100减20',
                'type': 'FULL_REDUCTION',
                'params': {'threshold': 100, 'discount': 20},
                'total_stock': 100,
                'remaining_stock': 100,
                'limit_per_user': 2,
                'validity_mode': 'RELATIVE',
                'validity_days': 3,
                'transferable': True,
                'shareable': True,
                'share_limit': 3,
            },
            {
                'name': '新人专享8折券',
                'description': '新注册用户专享折扣',
                'type': 'NEWCOMER',
                'params': {'discount_rate': 0.8},
                'total_stock': 50,
                'remaining_stock': 50,
                'limit_per_user': 1,
                'validity_mode': 'RELATIVE',
                'validity_days': 7,
                'transferable': False,
                'shareable': False,
            },
            {
                'name': '无门槛5元券',
                'description': '无门槛直减5元',
                'type': 'NO_THRESHOLD',
                'params': {'discount': 5},
                'total_stock': 200,
                'remaining_stock': 200,
                'limit_per_user': 3,
                'validity_mode': 'RELATIVE',
                'validity_days': 1,
                'transferable': True,
                'stackable': True,
                'shareable': True,
                'share_limit': 5,
            },
            {
                'name': '食品类满50减10',
                'description': '仅限食品品类使用',
                'type': 'CATEGORY',
                'params': {'category': '食品', 'threshold': 50, 'discount': 10},
                'total_stock': 80,
                'remaining_stock': 80,
                'limit_per_user': 1,
                'validity_mode': 'FIXED',
                'validity_days': None,
                'fixed_start_date': datetime.utcnow(),
                'fixed_end_date': datetime.utcnow() + timedelta(days=30),
            },
            {
                'name': '限时午餐券',
                'description': '每天11:00-13:00可用',
                'type': 'TIME_LIMITED',
                'params': {'start_hour': 11, 'end_hour': 13, 'discount': 8},
                'total_stock': 30,
                'remaining_stock': 30,
                'limit_per_user': 1,
                'validity_mode': 'RELATIVE',
                'validity_days': 1,
            },
        ]

        for c in campaigns:
            campaign = Campaign(
                id=str(uuid.uuid4()),
                name=c['name'],
                description=c.get('description', ''),
                type=c['type'],
                params_json=json.dumps(c['params'], ensure_ascii=False),
                total_stock=c['total_stock'],
                remaining_stock=c['remaining_stock'],
                limit_per_user=c.get('limit_per_user', 1),
                validity_mode=c.get('validity_mode', 'RELATIVE'),
                validity_days=c.get('validity_days', 1),
                fixed_start_date=c.get('fixed_start_date'),
                fixed_end_date=c.get('fixed_end_date'),
                transferable=c.get('transferable', False),
                stackable=c.get('stackable', False),
                shareable=c.get('shareable', False),
                share_limit=c.get('share_limit', 3),
                created_by=operator_id,
            )
            db.session.add(campaign)
            print(f"  Created campaign: {c['name']}")

        db.session.commit()
        print("\nSeed completed!")
        print("\nTest accounts:")
        print("  admin / admin123 (管理员)")
        print("  operator / operator123 (运营人员)")
        print("  verifier / verifier123 (核销人员)")
        print("  user1 / user123 (普通用户)")
        print("  user2 / user123 (普通用户)")
        print("  user3 / user123 (普通用户)")


if __name__ == '__main__':
    seed()
