"""Authentication routes."""
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    """Redirect to appropriate page based on login status and role."""
    if current_user.is_authenticated:
        role = current_user.role.lower()
        return redirect(f'/{role}')
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET'])
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET'])
def register():
    """Register page."""
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout and redirect to login."""
    logout_user()
    return redirect(url_for('auth.login'))
