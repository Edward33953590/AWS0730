"""Verifier routes - pages for coupon verifiers."""
from flask import Blueprint, render_template
from services.auth_service import role_required

verifier_bp = Blueprint('verifier', __name__)


@verifier_bp.route('/')
@role_required('VERIFIER')
def index():
    """Verifier homepage - redemption interface."""
    return render_template('verifier/index.html')


@verifier_bp.route('/records')
@role_required('VERIFIER')
def records():
    """Redemption records page."""
    return render_template('verifier/index.html')
