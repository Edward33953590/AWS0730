"""Share routes - public share link pages."""
from flask import Blueprint, render_template

share_bp = Blueprint('share', __name__)


@share_bp.route('/share/<share_code>')
def share_page(share_code):
    """Share link claim page."""
    return render_template('share.html', share_code=share_code)
