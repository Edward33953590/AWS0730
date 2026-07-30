"""User routes - pages for regular users."""
from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from services.auth_service import role_required
from models.coupon import Coupon
from models.campaign import Campaign

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


@user_bp.route('/coupons/<coupon_id>')
@role_required('USER')
def coupon_detail(coupon_id):
    """Coupon detail page with QR code."""
    coupon = Coupon.query.get(coupon_id)
    if not coupon:
        abort(404)
    if coupon.user_id != current_user.id:
        abort(403)

    campaign = Campaign.query.get(coupon.campaign_id)

    type_labels = {
        'FULL_REDUCTION': '满减', 'DISCOUNT': '折扣', 'NO_THRESHOLD': '无门槛',
        'ADD_ON': '加购', 'CATEGORY': '品类', 'NEWCOMER': '新人', 'TIME_LIMITED': '限时'
    }
    status_labels = {
        'CLAIMED': '待使用', 'REDEEMED': '已核销',
        'EXPIRED': '已过期', 'TRANSFERRED': '已转赠'
    }

    return render_template('user/coupon_detail.html',
                           coupon=coupon,
                           campaign=campaign,
                           type_label=type_labels.get(campaign.type, campaign.type) if campaign else '未知',
                           status_label=status_labels.get(coupon.status, coupon.status))


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
