"""Coupon service - core business logic for claiming coupons."""
import uuid
import string
import random
from datetime import datetime, timedelta
from sqlalchemy import text
from models.campaign import Campaign
from models.coupon import Coupon
from extensions import db


def generate_coupon_code():
    """Generate unique coupon code: CPN-XXXXXXXX (8 chars uppercase + digits)."""
    chars = string.ascii_uppercase + string.digits
    while True:
        code = 'CPN-' + ''.join(random.choices(chars, k=8))
        # Check uniqueness
        exists = Coupon.query.filter_by(coupon_code=code).first()
        if not exists:
            return code


def calculate_expiry(campaign):
    """Calculate coupon expiry based on campaign validity mode."""
    if campaign.validity_mode == 'FIXED':
        return campaign.fixed_end_date or (datetime.utcnow() + timedelta(days=1))
    else:
        days = campaign.validity_days or 1
        return datetime.utcnow() + timedelta(days=days)


def claim_coupon(user_id, campaign_id):
    """
    Claim a coupon from a campaign.
    Returns (coupon, error_message).
    Uses atomic stock decrement for concurrency safety.
    """
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return None, 'CAMPAIGN_NOT_FOUND', '活动不存在'

    # Check if campaign has started
    if campaign.start_time and datetime.utcnow() < campaign.start_time:
        return None, 'CAMPAIGN_NOT_STARTED', '活动未开始'

    # Check if campaign is a NEWCOMER type - only first-time users
    if campaign.type == 'NEWCOMER':
        # Check if user has any coupons already (not a newcomer)
        existing_coupons = Coupon.query.filter_by(user_id=user_id).count()
        if existing_coupons > 0:
            return None, 'NOT_NEWCOMER', '仅限新用户领取'

    # Check user limit
    user_claimed = Coupon.query.filter_by(
        campaign_id=campaign_id, user_id=user_id
    ).filter(Coupon.status != 'TRANSFERRED').count()

    if user_claimed >= campaign.limit_per_user:
        return None, 'ALREADY_CLAIMED', '已达到领取上限'

    # Risk check
    from services.risk_engine import check_risk
    risk_result = check_risk(user_id, action='CLAIM', campaign_id=campaign_id)
    if risk_result['decision'] == 'BLOCK':
        return None, 'RISK_BLOCKED', f"操作异常，已被拦截: {risk_result['reason']}"

    # Atomic stock decrement using raw SQL for concurrency safety
    result = db.session.execute(
        text("""
            UPDATE campaigns
            SET remaining_stock = remaining_stock - 1
            WHERE id = :campaign_id AND remaining_stock > 0
        """),
        {'campaign_id': campaign_id}
    )

    if result.rowcount == 0:
        db.session.rollback()
        return None, 'OUT_OF_STOCK', '库存不足'

    # Create coupon
    coupon = Coupon(
        id=str(uuid.uuid4()),
        coupon_code=generate_coupon_code(),
        campaign_id=campaign_id,
        user_id=user_id,
        status='CLAIMED',
        claimed_at=datetime.utcnow(),
        expires_at=calculate_expiry(campaign),
    )
    db.session.add(coupon)
    db.session.commit()

    # Log the operation
    from services.log_service import log_operation
    log_operation(user_id, 'CLAIM_COUPON', coupon.coupon_code,
                  {'campaign_id': campaign_id, 'campaign_name': campaign.name})

    # Notify user
    from services.notification_service import notify_claim_success
    notify_claim_success(user_id, campaign.name, coupon.coupon_code)

    return coupon, None, None


def get_user_coupons(user_id, status=None, page=1, page_size=20):
    """Get coupons belonging to a user."""
    query = Coupon.query.filter_by(user_id=user_id)

    if status:
        query = query.filter_by(status=status)

    # Auto-expire coupons past their expiry date
    now = datetime.utcnow()
    expired = Coupon.query.filter(
        Coupon.user_id == user_id,
        Coupon.status == 'CLAIMED',
        Coupon.expires_at < now
    ).all()
    for c in expired:
        c.status = 'EXPIRED'
    if expired:
        db.session.commit()

    query = query.order_by(Coupon.claimed_at.desc())
    total = query.count()
    coupons = query.offset((page - 1) * page_size).limit(page_size).all()

    # Enrich with campaign info
    items = []
    for coupon in coupons:
        item = coupon.to_dict()
        item['campaign_name'] = coupon.campaign.name if coupon.campaign else ''
        item['campaign_type'] = coupon.campaign.type if coupon.campaign else ''
        item['campaign_params'] = coupon.campaign.params if coupon.campaign else {}
        items.append(item)

    return {
        'items': items,
        'total': total,
        'page': page,
        'page_size': page_size,
    }
