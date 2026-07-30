"""JSON API routes - used by frontend AJAX calls."""
import uuid
from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from models.campaign import Campaign
from services.auth_service import role_required
from extensions import db

api_bp = Blueprint('api', __name__)


# ==================== Auth API ====================

@api_bp.route('/auth/register', methods=['POST'])
def api_register():
    """Register a new user."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': {'code': 'BAD_REQUEST', 'message': '请求数据无效'}}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'USER').upper()

    if not username or len(username) < 3 or len(username) > 20:
        return jsonify({'success': False, 'error': {'code': 'INVALID_INPUT', 'message': '用户名需3-20个字符'}}), 400
    if not password or len(password) < 6 or len(password) > 50:
        return jsonify({'success': False, 'error': {'code': 'INVALID_INPUT', 'message': '密码需6-50个字符'}}), 400
    if role not in ('ADMIN', 'OPERATOR', 'VERIFIER', 'USER'):
        return jsonify({'success': False, 'error': {'code': 'INVALID_INPUT', 'message': '无效的角色'}}), 400

    existing = User.query.filter_by(username=username).first()
    if existing:
        return jsonify({'success': False, 'error': {'code': 'USERNAME_EXISTS', 'message': '用户名已被占用'}}), 409

    user = User(id=str(uuid.uuid4()), username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    redirect_url = _get_role_redirect(role)
    return jsonify({'success': True, 'data': {'user': user.to_dict(), 'redirect': redirect_url}}), 201


@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    """Login with username and password."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': {'code': 'BAD_REQUEST', 'message': '请求数据无效'}}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not username or not password:
        return jsonify({'success': False, 'error': {'code': 'INVALID_INPUT', 'message': '请输入用户名和密码'}}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'error': {'code': 'INVALID_CREDENTIALS', 'message': '用户名或密码错误'}}), 401

    login_user(user)
    redirect_url = _get_role_redirect(user.role)
    return jsonify({'success': True, 'data': {'user': user.to_dict(), 'redirect': redirect_url}})


@api_bp.route('/auth/me')
@login_required
def api_me():
    return jsonify({'success': True, 'data': current_user.to_dict()})


@api_bp.route('/auth/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({'success': True, 'data': {'redirect': '/login'}})


# ==================== Campaigns API ====================

@api_bp.route('/campaigns', methods=['GET'])
@login_required
def list_campaigns():
    from services.campaign_service import list_campaigns as svc_list
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    coupon_type = request.args.get('type', None)
    active_only = request.args.get('active', 'false').lower() == 'true'
    result = svc_list(page=page, page_size=page_size, coupon_type=coupon_type, active_only=active_only)
    return jsonify({'success': True, 'data': result})


@api_bp.route('/campaigns/<campaign_id>', methods=['GET'])
@login_required
def get_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return jsonify({'success': False, 'error': {'code': 'NOT_FOUND', 'message': '活动不存在'}}), 404
    return jsonify({'success': True, 'data': campaign.to_dict()})


@api_bp.route('/campaigns', methods=['POST'])
@role_required('OPERATOR')
def create_campaign():
    from services.campaign_service import validate_campaign_data, create_campaign as svc_create
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': {'code': 'BAD_REQUEST', 'message': '请求数据无效'}}), 400
    cleaned, error = validate_campaign_data(data)
    if error:
        return jsonify({'success': False, 'error': {'code': 'INVALID_INPUT', 'message': error}}), 400
    campaign = svc_create(cleaned, current_user.id)
    return jsonify({'success': True, 'data': campaign.to_dict()}), 201


@api_bp.route('/campaigns/<campaign_id>', methods=['PUT'])
@role_required('OPERATOR')
def update_campaign(campaign_id):
    from services.campaign_service import update_campaign as svc_update
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': {'code': 'BAD_REQUEST', 'message': '请求数据无效'}}), 400
    campaign, error = svc_update(campaign_id, data)
    if error:
        return jsonify({'success': False, 'error': {'code': 'INVALID_INPUT', 'message': error}}), 400
    return jsonify({'success': True, 'data': campaign.to_dict()})


@api_bp.route('/campaigns/<campaign_id>', methods=['DELETE'])
@role_required('OPERATOR')
def delete_campaign(campaign_id):
    from services.campaign_service import delete_campaign as svc_delete
    success, error = svc_delete(campaign_id)
    if not success:
        return jsonify({'success': False, 'error': {'code': 'DELETE_FAILED', 'message': error}}), 400
    return jsonify({'success': True, 'data': {'message': '删除成功'}})


@api_bp.route('/campaigns/defaults/<coupon_type>', methods=['GET'])
@login_required
def get_campaign_defaults(coupon_type):
    from services.campaign_service import get_default_params, VALID_TYPES
    if coupon_type not in VALID_TYPES:
        return jsonify({'success': False, 'error': {'code': 'INVALID_TYPE', 'message': '无效类型'}}), 400
    return jsonify({'success': True, 'data': get_default_params(coupon_type)})


# ==================== AI / Risk API ====================

@api_bp.route('/ai/risk-check', methods=['POST'])
@login_required
def risk_check():
    from services.risk_engine import check_risk
    data = request.get_json() or {}
    user_id = data.get('user_id', current_user.id)
    action = data.get('action', 'CLAIM')
    campaign_id = data.get('campaign_id')
    result = check_risk(user_id, action=action, campaign_id=campaign_id)
    return jsonify({'success': True, 'data': result})


@api_bp.route('/ai/recommend', methods=['POST'])
@role_required('USER')
def ai_recommend():
    from services.ai_recommend_service import get_recommendations
    result = get_recommendations(current_user.id)
    return jsonify({'success': True, 'data': result})


@api_bp.route('/ai/generate-copy', methods=['POST'])
@role_required('OPERATOR')
def ai_generate_copy():
    from services.ai_copy_service import generate_copy
    data = request.get_json() or {}
    coupon_type = data.get('type', 'FULL_REDUCTION')
    params = data.get('params', {})
    context = data.get('context', '')
    result = generate_copy(coupon_type, params, context)
    return jsonify({'success': True, 'data': result})


@api_bp.route('/ai/user-profile/<user_id>', methods=['GET'])
@role_required('ADMIN')
def ai_user_profile(user_id):
    from services.ai_profile_service import get_user_profile
    result = get_user_profile(user_id)
    return jsonify({'success': True, 'data': result})


@api_bp.route('/ai/models', methods=['GET'])
@role_required('ADMIN')
def ai_models():
    from services.bedrock_service import bedrock_service
    models = bedrock_service.list_models()
    return jsonify({'success': True, 'data': models})


# ==================== Logs API ====================

@api_bp.route('/logs', methods=['GET'])
@role_required('ADMIN')
def get_logs():
    from services.log_service import get_logs as svc_get_logs
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 50, type=int)
    action = request.args.get('action', None)
    user_id_param = request.args.get('userId', None)
    result = svc_get_logs(page=page, page_size=page_size, action=action, user_id=user_id_param)
    return jsonify({'success': True, 'data': result})


# ==================== Redemption API ====================

@api_bp.route('/redeem/online-requests', methods=['GET'])
@role_required('VERIFIER')
def online_redeem_requests():
    """Get pending online redemption requests for verifiers."""
    from models.notification import Notification
    notifs = Notification.query.filter_by(
        user_id=current_user.id,
        type='ONLINE_REDEEM_REQUEST',
        read=False
    ).order_by(Notification.created_at.desc()).limit(50).all()
    items = []
    for n in notifs:
        items.append({
            'id': n.id,
            'content': n.content,
            'created_at': n.created_at.isoformat() if n.created_at else None,
        })
    return jsonify({'success': True, 'data': {'items': items}})


@api_bp.route('/redeem', methods=['POST'])
@role_required('VERIFIER')
def redeem_coupon():
    from services.redemption_service import redeem_coupon as svc_redeem
    data = request.get_json()
    if not data or not data.get('coupon_code'):
        return jsonify({'success': False, 'error': {'code': 'BAD_REQUEST', 'message': '请输入券码'}}), 400
    coupon_code = data['coupon_code'].strip().upper()
    result, error_code, error_msg, status = svc_redeem(coupon_code, current_user.id)
    if error_code:
        if error_code == 'ALREADY_REDEEMED' and result:
            return jsonify({'success': True, 'data': result}), 200
        return jsonify({'success': False, 'error': {'code': error_code, 'message': error_msg}}), status
    return jsonify({'success': True, 'data': result})


@api_bp.route('/redeem/records', methods=['GET'])
@role_required('VERIFIER')
def redemption_records():
    from services.redemption_service import get_redemption_records
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    result = get_redemption_records(current_user.id, page=page, page_size=page_size)
    return jsonify({'success': True, 'data': result})


# ==================== Coupons API ====================

@api_bp.route('/coupons/submit-redeem', methods=['POST'])
@role_required('USER')
def submit_online_redeem():
    """User submits coupon for online redemption - notifies all verifiers."""
    from models.coupon import Coupon
    from models.notification import Notification
    from services.notification_service import create_notification
    data = request.get_json()
    if not data or not data.get('coupon_code'):
        return jsonify({'success': False, 'error': {'code': 'BAD_REQUEST', 'message': '请提供券码'}}), 400
    coupon_code = data['coupon_code'].strip().upper()
    coupon = Coupon.query.filter_by(coupon_code=coupon_code, user_id=current_user.id).first()
    if not coupon:
        return jsonify({'success': False, 'error': {'code': 'NOT_FOUND', 'message': '券码不存在或不属于当前用户'}}), 404
    if coupon.status != 'CLAIMED':
        return jsonify({'success': False, 'error': {'code': 'INVALID_STATUS', 'message': '该券已核销或已过期'}}), 400
    if coupon.is_expired:
        return jsonify({'success': False, 'error': {'code': 'EXPIRED', 'message': '该券已过期'}}), 400
    # Check if already submitted (unread notification exists for this code)
    existing = Notification.query.filter(
        Notification.type == 'ONLINE_REDEEM_REQUEST',
        Notification.read == False,
        Notification.content.contains(coupon_code)
    ).first()
    if existing:
        return jsonify({'success': False, 'error': {'code': 'ALREADY_SUBMITTED', 'message': '已提交核销请求，请等待核销人员处理'}}), 409
    # Notify all verifiers
    verifiers = User.query.filter_by(role='VERIFIER').all()
    campaign_name = ''
    if coupon.campaign:
        campaign_name = coupon.campaign.name
    for v in verifiers:
        create_notification(
            v.id,
            'ONLINE_REDEEM_REQUEST',
            f'用户 {current_user.username} 提交了线上核销请求，券码: {coupon_code}，活动: {campaign_name}'
        )
    from services.log_service import log_operation
    log_operation(current_user.id, 'SUBMIT_ONLINE_REDEEM', coupon_code, {'campaign_name': campaign_name})
    return jsonify({'success': True, 'data': {'message': '已通知核销人员'}})


@api_bp.route('/coupons/claim', methods=['POST'])
@role_required('USER')
def claim_coupon():
    from services.coupon_service import claim_coupon as svc_claim
    data = request.get_json()
    if not data or not data.get('campaign_id'):
        return jsonify({'success': False, 'error': {'code': 'BAD_REQUEST', 'message': '缺少活动ID'}}), 400
    coupon, error_code, error_msg = svc_claim(current_user.id, data['campaign_id'])
    if error_code:
        status = 409
        if error_code == 'CAMPAIGN_NOT_FOUND':
            status = 404
        elif error_code == 'CAMPAIGN_NOT_STARTED':
            status = 400
        return jsonify({'success': False, 'error': {'code': error_code, 'message': error_msg}}), status
    return jsonify({'success': True, 'data': {'coupon_id': coupon.id, 'coupon_code': coupon.coupon_code, 'expires_at': coupon.expires_at.isoformat()}}), 201


@api_bp.route('/coupons/my', methods=['GET'])
@role_required('USER')
def my_coupons():
    from services.coupon_service import get_user_coupons
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    status = request.args.get('status', None)
    result = get_user_coupons(current_user.id, status=status, page=page, page_size=page_size)
    return jsonify({'success': True, 'data': result})


@api_bp.route('/coupons/transfer', methods=['POST'])
@role_required('USER')
def transfer_coupon():
    from services.share_service import transfer_coupon as svc_transfer
    data = request.get_json() or {}
    coupon_id = data.get('coupon_id')
    target_username = data.get('target_username', '').strip()
    if not coupon_id or not target_username:
        return jsonify({'success': False, 'error': {'code': 'BAD_REQUEST', 'message': '缺少参数'}}), 400
    result, error = svc_transfer(coupon_id, current_user.id, target_username)
    if error:
        return jsonify({'success': False, 'error': {'code': 'TRANSFER_FAILED', 'message': error}}), 400
    return jsonify({'success': True, 'data': result})


@api_bp.route('/coupons/share', methods=['POST'])
@role_required('USER')
def create_share():
    from services.share_service import create_share_link
    data = request.get_json() or {}
    campaign_id = data.get('campaign_id')
    if not campaign_id:
        return jsonify({'success': False, 'error': {'code': 'BAD_REQUEST', 'message': '缺少活动ID'}}), 400
    result, error = create_share_link(campaign_id, current_user.id)
    if error:
        return jsonify({'success': False, 'error': {'code': 'SHARE_FAILED', 'message': error}}), 400
    return jsonify({'success': True, 'data': result})


@api_bp.route('/coupons/claim-share/<share_code>', methods=['POST'])
@role_required('USER')
def claim_share(share_code):
    from services.share_service import claim_by_share
    coupon, error_code, error_msg = claim_by_share(share_code, current_user.id)
    if error_code:
        return jsonify({'success': False, 'error': {'code': error_code, 'message': error_msg}}), 400
    return jsonify({'success': True, 'data': {'coupon_code': coupon.coupon_code}})


@api_bp.route('/coupons/ranking', methods=['GET'])
@login_required
def coupon_ranking():
    campaigns = Campaign.query.all()
    ranked = sorted(campaigns, key=lambda c: c.total_stock - c.remaining_stock, reverse=True)[:10]
    result = [{'id': c.id, 'name': c.name, 'type': c.type, 'claimed': c.total_stock - c.remaining_stock, 'remaining_stock': c.remaining_stock, 'total_stock': c.total_stock} for c in ranked]
    return jsonify({'success': True, 'data': result})


# ==================== Blacklist API ====================

@api_bp.route('/blacklist', methods=['GET'])
@role_required('OPERATOR')
def get_blacklist():
    from models.blacklist import BlackWhiteList
    list_type = request.args.get('type', None)
    query = BlackWhiteList.query
    if list_type:
        query = query.filter_by(type=list_type.upper())
    entries = query.order_by(BlackWhiteList.created_at.desc()).all()
    items = [{'id': e.id, 'user_id': e.user_id, 'username': e.target_user.username if e.target_user else '', 'type': e.type, 'reason': e.reason, 'created_at': e.created_at.isoformat()} for e in entries]
    return jsonify({'success': True, 'data': {'items': items}})


@api_bp.route('/blacklist', methods=['POST'])
@role_required('OPERATOR')
def add_blacklist():
    import uuid as uuid_mod
    from models.blacklist import BlackWhiteList
    from models.user import User as UserModel
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    list_type = data.get('type', 'BLACK').upper()
    reason = data.get('reason', '').strip()
    if not username or not reason:
        return jsonify({'success': False, 'error': {'code': 'BAD_REQUEST', 'message': '请填写用户名和原因'}}), 400
    if list_type not in ('BLACK', 'WHITE'):
        return jsonify({'success': False, 'error': {'code': 'BAD_REQUEST', 'message': '类型无效'}}), 400
    target = UserModel.query.filter_by(username=username).first()
    if not target:
        return jsonify({'success': False, 'error': {'code': 'NOT_FOUND', 'message': '用户不存在'}}), 404
    existing = BlackWhiteList.query.filter_by(user_id=target.id, type=list_type).first()
    if existing:
        return jsonify({'success': False, 'error': {'code': 'DUPLICATE', 'message': '该用户已在名单中'}}), 409
    entry = BlackWhiteList(id=str(uuid_mod.uuid4()), user_id=target.id, type=list_type, reason=reason, created_by=current_user.id)
    db.session.add(entry)
    db.session.commit()
    from services.log_service import log_operation
    log_operation(current_user.id, f'ADD_{list_type}LIST', username, {'reason': reason})
    return jsonify({'success': True, 'data': {'message': '添加成功'}}), 201


@api_bp.route('/blacklist/<entry_id>', methods=['DELETE'])
@role_required('OPERATOR')
def remove_blacklist(entry_id):
    from models.blacklist import BlackWhiteList
    entry = BlackWhiteList.query.get(entry_id)
    if entry:
        from services.log_service import log_operation
        log_operation(current_user.id, f'REMOVE_{entry.type}LIST', entry.user_id)
        db.session.delete(entry)
        db.session.commit()
    return jsonify({'success': True, 'data': {'message': '已移除'}})


# ==================== Stats API ====================

@api_bp.route('/stats/overview', methods=['GET'])
@role_required('ADMIN')
def stats_overview():
    from services.stats_service import get_overview
    result = get_overview()
    return jsonify({'success': True, 'data': result})


@api_bp.route('/stats/export', methods=['GET'])
@role_required('ADMIN')
def stats_export():
    import csv
    import io
    from flask import Response
    from models.coupon import Coupon
    output = io.StringIO()
    # Add UTF-8 BOM for Excel compatibility
    output.write('\ufeff')
    writer = csv.writer(output)
    writer.writerow(['券码', '活动名称', '用户ID', '状态', '领取时间', '过期时间'])
    coupons = Coupon.query.order_by(Coupon.claimed_at.desc()).limit(1000).all()
    for c in coupons:
        writer.writerow([c.coupon_code, c.campaign.name if c.campaign else '', c.user_id, c.status, c.claimed_at.isoformat() if c.claimed_at else '', c.expires_at.isoformat() if c.expires_at else ''])
    output.seek(0)
    return Response(output.getvalue().encode('utf-8'), mimetype='text/csv; charset=utf-8', headers={'Content-Disposition': 'attachment; filename=export.csv'})


# ==================== Favorites API ====================

@api_bp.route('/favorites', methods=['GET'])
@role_required('USER')
def get_favorites():
    from models.favorite import Favorite
    favs = Favorite.query.filter_by(user_id=current_user.id).all()
    items = []
    for f in favs:
        item = f.to_dict()
        camp = Campaign.query.get(f.campaign_id)
        item['campaign_name'] = camp.name if camp else ''
        items.append(item)
    return jsonify({'success': True, 'data': {'items': items}})


@api_bp.route('/favorites', methods=['POST'])
@role_required('USER')
def add_favorite():
    import uuid as uuid_mod
    from models.favorite import Favorite
    data = request.get_json() or {}
    campaign_id = data.get('campaign_id')
    if not campaign_id:
        return jsonify({'success': False, 'error': {'code': 'BAD_REQUEST', 'message': '缺少活动ID'}}), 400
    existing = Favorite.query.filter_by(user_id=current_user.id, campaign_id=campaign_id).first()
    if not existing:
        fav = Favorite(id=str(uuid_mod.uuid4()), user_id=current_user.id, campaign_id=campaign_id)
        db.session.add(fav)
        db.session.commit()
    return jsonify({'success': True, 'data': {'message': '收藏成功'}})


@api_bp.route('/favorites/<fav_id>', methods=['DELETE'])
@role_required('USER')
def remove_favorite(fav_id):
    from models.favorite import Favorite
    fav = Favorite.query.filter_by(id=fav_id, user_id=current_user.id).first()
    if not fav:
        fav = Favorite.query.filter_by(campaign_id=fav_id, user_id=current_user.id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
    return jsonify({'success': True, 'data': {'message': '已取消收藏'}})


# ==================== Notifications API ====================

@api_bp.route('/notifications/unread-count')
def notifications_unread_count():
    if not current_user.is_authenticated:
        return jsonify({'success': True, 'data': {'count': 0}})
    from models.notification import Notification
    count = Notification.query.filter_by(user_id=current_user.id, read=False).count()
    return jsonify({'success': True, 'data': {'count': count}})


@api_bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    from models.notification import Notification
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(50).all()
    return jsonify({'success': True, 'data': {'items': [n.to_dict() for n in notifs]}})


@api_bp.route('/notifications/<notif_id>/read', methods=['PUT'])
@login_required
def mark_notification_read(notif_id):
    from models.notification import Notification
    n = Notification.query.filter_by(id=notif_id, user_id=current_user.id).first()
    if n:
        n.read = True
        db.session.commit()
    return jsonify({'success': True})


@api_bp.route('/notifications/read-all', methods=['PUT'])
@login_required
def mark_all_read():
    from models.notification import Notification
    Notification.query.filter_by(user_id=current_user.id, read=False).update({'read': True})
    db.session.commit()
    return jsonify({'success': True})


# ==================== Health ====================

@api_bp.route('/health')
def health():
    return jsonify({'success': True, 'message': 'Coupon Center API is running'})


# ==================== Helpers ====================

def _get_role_redirect(role):
    redirects = {'ADMIN': '/admin', 'OPERATOR': '/operator', 'VERIFIER': '/verifier', 'USER': '/user'}
    return redirects.get(role, '/user')
