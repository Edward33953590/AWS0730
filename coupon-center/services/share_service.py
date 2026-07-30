"""Share and transfer service."""
import uuid
import string
import random
from datetime import datetime, timedelta
from models.coupon import Coupon
from models.campaign import Campaign
from models.share_link import ShareLink
from models.user import User
from extensions import db


def transfer_coupon(coupon_id, from_user_id, target_username):
    """Transfer a coupon to another user. Returns (result, error)."""
    coupon = Coupon.query.filter_by(id=coupon_id, user_id=from_user_id).first()
    if not coupon:
        return None, '优惠券不存在或不属于你'

    if coupon.status != 'CLAIMED':
        return None, '该券状态不可转赠'

    if coupon.is_expired:
        return None, '该券已过期'

    campaign = Campaign.query.get(coupon.campaign_id)
    if not campaign or not campaign.transferable:
        return None, '该券不可转赠'

    target_user = User.query.filter_by(username=target_username).first()
    if not target_user:
        return None, '目标用户不存在'

    if target_user.id == from_user_id:
        return None, '不能转赠给自己'

    # Perform transfer
    coupon.status = 'TRANSFERRED'

    new_coupon = Coupon(
        id=str(uuid.uuid4()),
        coupon_code=coupon.coupon_code,  # Keep same code
        campaign_id=coupon.campaign_id,
        user_id=target_user.id,
        status='CLAIMED',
        claimed_at=datetime.utcnow(),
        expires_at=coupon.expires_at,  # Keep same expiry
        transferred_from=from_user_id,
    )
    # Update old coupon code to avoid unique conflict
    coupon.coupon_code = coupon.coupon_code + '-T'

    db.session.add(new_coupon)
    db.session.commit()

    # Notifications
    from services.notification_service import notify_transfer_received
    from_user = User.query.get(from_user_id)
    notify_transfer_received(target_user.id, from_user.username, campaign.name)

    # Log
    from services.log_service import log_operation
    log_operation(from_user_id, 'TRANSFER_COUPON', new_coupon.coupon_code,
                  {'to_user': target_username, 'campaign': campaign.name})

    return {'coupon_code': new_coupon.coupon_code, 'target_user': target_username}, None


def create_share_link(campaign_id, user_id):
    """Create a share link for a campaign. Returns (share_link, error)."""
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return None, '活动不存在'
    if not campaign.shareable:
        return None, '该活动不支持分享'

    share_code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    link = ShareLink(
        id=str(uuid.uuid4()),
        campaign_id=campaign_id,
        created_by=user_id,
        share_code=share_code,
        max_claims=campaign.share_limit,
        current_claims=0,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.session.add(link)
    db.session.commit()

    return {'share_code': share_code, 'max_claims': campaign.share_limit}, None


def claim_by_share(share_code, user_id):
    """Claim a coupon via share link. Returns (coupon, error_code, error_msg)."""
    link = ShareLink.query.filter_by(share_code=share_code).first()
    if not link:
        return None, 'INVALID_LINK', '无效的分享链接'

    if link.expires_at and datetime.utcnow() > link.expires_at:
        return None, 'LINK_EXPIRED', '链接已过期'

    if link.current_claims >= link.max_claims:
        return None, 'LINK_EXHAUSTED', '分享次数已用完'

    # Use normal claim logic
    from services.coupon_service import claim_coupon
    coupon, error_code, error_msg = claim_coupon(user_id, link.campaign_id)

    if coupon:
        link.current_claims += 1
        db.session.commit()

    return coupon, error_code, error_msg
