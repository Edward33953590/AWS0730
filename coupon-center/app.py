"""优惠券发放与核销中心 - Flask Application"""
from flask import Flask
from config import Config
from extensions import db, migrate, login_manager, csrf


def create_app(config_class=Config):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Login manager config
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'

    # Register blueprints
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.operator import operator_bp
    from routes.verifier import verifier_bp
    from routes.admin import admin_bp
    from routes.api import api_bp
    from routes.share import share_bp
    from routes.scan import scan_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(operator_bp, url_prefix='/operator')
    app.register_blueprint(verifier_bp, url_prefix='/verifier')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(share_bp)
    app.register_blueprint(scan_bp)

    # Exempt API from CSRF (uses JWT)
    csrf.exempt(api_bp)

    # Create tables
    with app.app_context():
        from models import user, campaign, coupon, redemption
        from models import notification, risk_log, operation_log
        from models import share_link, blacklist, template, favorite
        from models import poster_asset
        db.create_all()

    return app


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    return User.query.get(user_id)


if __name__ == '__main__':
    app = create_app()
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', debug=True, port=5000)
