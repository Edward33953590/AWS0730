"""User routes - pages for regular users."""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from services.auth_service import role_required

user_bp = Blueprint('user', __name__)


@user_bp.route('/')
@role_required('USER')
def index():
    """User homepage with AI recommendations."""
    return render_template('user/index.html')


@user_bp.route('/explore')
@role_required('USER')
def explore():
    """Browse all available coupons."""
    return render_template('user/explore.html')


@user_bp.route('/coupons')
@role_required('USER')
def coupons():
    """My coupon wallet."""
    return render_template('user/coupons.html')


@user_bp.route('/favorites')
@role_required('USER')
def favorites():
    """Favorites page."""
    return render_template('user/favorites.html')


@user_bp.route('/ranking')
@role_required('USER')
def ranking():
    """Ranking page."""
    return render_template('user/ranking.html')


@user_bp.route('/notifications')
@role_required('USER')
def notifications():
    """Notifications page."""
    return render_template('user/notifications.html')
