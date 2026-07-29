"""Debug login issue - run against live server context."""
import traceback
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models.user import User

app = create_app()
app.config['TESTING'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True

with app.app_context():
    # Check if admin user exists
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"Admin user found: id={admin.id}, role={admin.role}")
        print(f"Password check: {admin.check_password('admin123')}")
    else:
        print("ERROR: Admin user NOT found in database!")
        print("All users:")
        for u in User.query.all():
            print(f"  {u.username} ({u.role})")

# Now test the actual login route
with app.test_client() as c:
    try:
        r = c.post('/api/auth/login', json={'username': 'admin', 'password': 'admin123'})
        print(f"\nTest client result: {r.status_code}")
        print(r.get_json())
    except Exception as e:
        print(f"\nException: {e}")
        traceback.print_exc()
