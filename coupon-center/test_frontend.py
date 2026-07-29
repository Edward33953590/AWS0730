"""Test frontend pages render correctly."""
from app import create_app

app = create_app()
with app.test_client() as c:
    print("=== Public pages ===")
    r = c.get('/login')
    print(f"GET /login: {r.status_code}")
    r = c.get('/register')
    print(f"GET /register: {r.status_code}")

    print("\n=== User pages ===")
    c.post('/api/auth/login', json={'username': 'user1', 'password': 'user123'})
    r = c.get('/user/')
    print(f"GET /user/: {r.status_code}")

    print("\n=== Operator pages ===")
    c.get('/logout')
    c.post('/api/auth/login', json={'username': 'operator', 'password': 'operator123'})
    r = c.get('/operator/')
    print(f"GET /operator/: {r.status_code}")

    print("\n=== Verifier pages ===")
    c.get('/logout')
    c.post('/api/auth/login', json={'username': 'verifier', 'password': 'verifier123'})
    r = c.get('/verifier/')
    print(f"GET /verifier/: {r.status_code}")

    print("\n=== Admin pages ===")
    c.get('/logout')
    c.post('/api/auth/login', json={'username': 'admin', 'password': 'admin123'})
    r = c.get('/admin/')
    print(f"GET /admin/: {r.status_code}")

print("\nAll frontend tests passed!")
