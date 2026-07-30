"""Scan routes — QR code scan landing page.

Registered at root level so /v/CPN-XXXX is a short, scannable URL.
"""
import logging
from flask import Blueprint, render_template, redirect, flash
from flask_login import current_user
from models.coupon import Coupon

logger = logging.getLogger(__name__)

scan_bp = Blueprint('scan', __name__)


@scan_bp.route('/v/<coupon_code>')
def scan_landing(coupon_code):
    """Scan landing page — opened when a verifier scans a QR code.

    Three-way branch:
    1. Already authenticated + role=VERIFIER → auto-redeem result page
    2. Not authenticated → embedded login page (login then auto-redeem)
    3. Authenticated but not VERIFIER → error, redirect to login
    """
    code = coupon_code.strip().upper()
    coupon = Coupon.query.filter_by(coupon_code=code).first()
    if not coupon:
        logger.warning(f'扫码落地页: 券码不存在 code={code}')
        flash(f'券码 {code} 不存在', 'error')
        return render_template('verifier/scan_result.html', coupon_code=code, precheck_error='券码不存在')

    logger.info(f'扫码落地页: code={code}, coupon_status={coupon.status}, '
                f'user_authenticated={current_user.is_authenticated}, '
                f'user_role={current_user.role if current_user.is_authenticated else "N/A"}')

    if not current_user.is_authenticated:
        logger.info(f'扫码落地页: 未登录，跳转到登录页 code={code}')
        return render_template('verifier/scan_login.html', coupon_code=code)
    if current_user.role != 'VERIFIER':
        logger.warning(f'扫码落地页: 用户角色非核销员 role={current_user.role}')
        flash('需要核销员权限才能核销，请使用核销员账号登录', 'error')
        return redirect('/auth/login')

    logger.info(f'扫码落地页: 已登录核销员，进行自动核销 code={code}')
    return render_template('verifier/scan_result.html', coupon_code=code, precheck_error='')
