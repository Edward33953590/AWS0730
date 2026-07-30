"""Admin routes - pages for administrators."""
from flask import Blueprint, render_template
from services.auth_service import role_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@role_required('ADMIN')
def index():
    """Admin homepage - dashboard."""
    return render_template('admin/dashboard.html')


@admin_bp.route('/dashboard/live')
@role_required('ADMIN')
def live_dashboard():
    """Real-time data visualization dashboard."""
    return render_template('admin/live_dashboard.html')


@admin_bp.route('/ai-impact')
@role_required('ADMIN')
def ai_impact():
    """AI effect comparison lab."""
    return render_template('admin/ai_impact.html')


@admin_bp.route('/team')
@role_required('ADMIN')
def team():
    """Team contribution wall."""
    return render_template('admin/team_wall.html')


@admin_bp.route('/logs')
@role_required('ADMIN')
def logs():
    """Operation logs page."""
    return render_template('admin/logs.html')


@admin_bp.route('/risk')
@role_required('ADMIN')
def risk():
    """Risk monitoring page."""
    return render_template('admin/risk.html')


@admin_bp.route('/export')
@role_required('ADMIN')
def export():
    """Data export page."""
    return render_template('admin/export.html')


@admin_bp.route('/profiles')
@role_required('ADMIN')
def profiles():
    """User profiles page."""
    return render_template('admin/profiles.html')
