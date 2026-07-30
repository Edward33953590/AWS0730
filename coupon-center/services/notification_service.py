"""Notification service - create and manage notifications."""
import uuid
from datetime import datetime
from models.notification import Notification
from extensions import db


def create_notification(user_id, notif_type, content):
    """Create a notification for a user. Best effort (non-blocking)."""
    try:
        notif = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=notif_type,
            content=content,
            read=False,
            created_at=datetime.utcnow(),
        )
        db.session.add(notif)
        db.session.commit()
    except Exception:
        db.session.rollback()


def notify_claim_success(user_id, campaign_name, coupon_code):
    """Notify user of successful coupon claim."""
    create_notification(user_id, 'CLAIM_SUCCESS', f'成功领取「{campaign_name}」，券码: {coupon_code}')


def notify_transfer_received(user_id, from_username, campaign_name):
    """Notify user of received transfer."""
    create_notification(user_id, 'TRANSFER_RECEIVED', f'{from_username} 转赠了「{campaign_name}」给你')


def notify_risk_blocked(user_id, reason):
    """Notify user of risk block."""
    create_notification(user_id, 'RISK_BLOCKED', f'您的操作被风控拦截: {reason}')
