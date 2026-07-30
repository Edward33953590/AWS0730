"""Redemption service - coupon verification/redemption logic."""
import uuid
from datetime import datetime
from models.coupon import Coupon
from models.redemption import Redemption
from extensions import db


def redeem_coupon(coupon_code, verifier_id):
    """
    Redeem a coupon by code. Idempotent - returns same result on repeat calls.
    Returns (result_dict, error_code, error_message, http_status).
    """
    coupon = Coupon.query.filter_by(coupon_code=coupon_code).first()
    if not coupon:
        return None, 'INVALID_CODE', '无效券码', 404

    # Check if already redeemed (idempotent)
    if coupon.status == 'REDEEMED':
        existing = Redemption.query.filter_by(coupon_id=coupon.id).first()
        return {
            'status': 'ALREADY_REDEEMED',
            'coupon_code': coupon_code,
            'campaign_name': coupon.campaign.name if coupon.campaign else '',
            'redeemed_at': existing.redeemed_at.isoformat() if existing else None,
            'message': '该券已核销',
        }, 'ALREADY_REDEEMED', '已核销', 409

    # Check if expired
    if coupon.expires_at and datetime.utcnow() > coupon.expires_at:
        coupon.status = 'EXPIRED'
        db.session.commit()
        return None, 'COUPON_EXPIRED', '券已过期', 410

    # Check if transferred
    if coupon.status == 'TRANSFERRED':
        return None, 'COUPON_TRANSFERRED', '该券已转赠', 400

    # Check status is CLAIMED
    if coupon.status != 'CLAIMED':
        return None, 'INVALID_STATUS', f'券状态异常: {coupon.status}', 400

    # Perform redemption
    now = datetime.utcnow()
    coupon.status = 'REDEEMED'
    coupon.used_at = now

    redemption = Redemption(
        id=str(uuid.uuid4()),
        coupon_id=coupon.id,
        coupon_code=coupon_code,
        redeemed_by=verifier_id,
        redeemed_at=now,
    )
    db.session.add(redemption)
    db.session.commit()

    # Log the operation
    from services.log_service import log_operation
    log_operation(verifier_id, 'REDEEM_COUPON', coupon_code,
                  {'campaign_name': coupon.campaign.name if coupon.campaign else ''})

    result = {
        'status': 'REDEEMED',
        'coupon_code': coupon_code,
        'campaign_name': coupon.campaign.name if coupon.campaign else '',
        'redeemed_at': now.isoformat(),
    }
    return result, None, None, 200


def get_redemption_records(verifier_id, page=1, page_size=20):
    """Get redemption records for a verifier."""
    query = Redemption.query.filter_by(redeemed_by=verifier_id)
    query = query.order_by(Redemption.redeemed_at.desc())
    total = query.count()
    records = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for r in records:
        item = r.to_dict()
        if r.coupon and r.coupon.campaign:
            item['campaign_name'] = r.coupon.campaign.name
        else:
            item['campaign_name'] = ''
        items.append(item)

    return {
        'items': items,
        'total': total,
        'page': page,
        'page_size': page_size,
    }
