"""Coupon model."""
from datetime import datetime
from extensions import db


class Coupon(db.Model):
    """Coupon instance - individual coupons claimed by users."""
    __tablename__ = 'coupons'

    id = db.Column(db.String(36), primary_key=True)
    coupon_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='CLAIMED')
    # CLAIMED, REDEEMED, EXPIRED, TRANSFERRED
    claimed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    transferred_from = db.Column(db.String(36), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Index for common queries
    __table_args__ = (
        db.Index('idx_coupon_user_status', 'user_id', 'status'),
        db.Index('idx_coupon_campaign_user', 'campaign_id', 'user_id'),
    )

    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def to_dict(self):
        return {
            'id': self.id,
            'coupon_code': self.coupon_code,
            'campaign_id': self.campaign_id,
            'user_id': self.user_id,
            'status': self.status,
            'claimed_at': self.claimed_at.isoformat() if self.claimed_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'transferred_from': self.transferred_from,
            'is_expired': self.is_expired,
        }
