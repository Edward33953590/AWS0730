"""Operator routes - pages for campaign operators."""
from flask import Blueprint, render_template
from services.auth_service import role_required

operator_bp = Blueprint('operator', __name__)


@operator_bp.route('/')
@role_required('OPERATOR')
def index():
    """Operator homepage - redirect to campaigns."""
    return render_template('operator/campaigns.html')


@operator_bp.route('/campaigns')
@role_required('OPERATOR')
def campaigns():
    """Campaign list page."""
    return render_template('operator/campaigns.html')


@operator_bp.route('/campaigns/create')
@role_required('OPERATOR')
def create_campaign():
    """Create campaign page."""
    return render_template('operator/create.html')


@operator_bp.route('/campaigns/<campaign_id>')
@role_required('OPERATOR')
def edit_campaign(campaign_id):
    """Edit campaign page."""
    return render_template('operator/edit.html', campaign_id=campaign_id)


@operator_bp.route('/templates')
@role_required('OPERATOR')
def templates():
    """Campaign templates page."""
    return render_template('operator/templates.html')


@operator_bp.route('/batch')
@role_required('OPERATOR')
def batch():
    """Batch send coupons page."""
    return render_template('operator/batch.html')


@operator_bp.route('/blacklist')
@role_required('OPERATOR')
def blacklist():
    """Blacklist management page."""
    return render_template('operator/blacklist.html')
