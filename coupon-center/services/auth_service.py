"""Authentication service - role guards and utilities."""
from functools import wraps
from flask import jsonify, redirect, url_for, request
from flask_login import current_user


def role_required(*roles):
    """Decorator to restrict access to specific roles.
    
    Usage:
        @role_required('ADMIN', 'OPERATOR')
        def some_view():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                # API routes return JSON, page routes redirect
                if request.path.startswith('/api/'):
                    return jsonify({'success': False, 'error': {'code': 'UNAUTHORIZED', 'message': '请先登录'}}), 401
                return redirect(url_for('auth.login'))
            
            if current_user.role not in roles:
                if request.path.startswith('/api/'):
                    return jsonify({'success': False, 'error': {'code': 'FORBIDDEN', 'message': '无权限访问'}}), 403
                # Redirect to their own home page
                return redirect(url_for(f'{current_user.role.lower()}.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_current_user_or_401():
    """Get current user or return 401 error dict."""
    if not current_user.is_authenticated:
        return None
    return current_user
