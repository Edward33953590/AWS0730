"""Redemption model."""
from datetime import datetime
from extensions import db


class Redemption(db.Model):
    """Redemption record - tracks coupon redemptions."""
    __tablename__ = 'redemptions'

    id = db.Column(db.String(36), primary_key=True)
    coupon_id = db.Column(db.String(36), db.ForeignKey('coupons.id'), unique=True, nullable=False)
    coupon_code = db.Column(db.String(20), nullable=False)
    redeemed_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    redeemed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    coupon = db.relationship('Coupon', backref=db.backref('redemption', uselist=False))

    def to_dict(self):
        return {
            'id': self.id,
            'coupon_id': self.coupon_id,
            'coupon_code': self.coupon_code,
            'redeemed_by': self.redeemed_by,
            'redeemed_at': self.redeemed_at.isoformat() if self.redeemed_at else None,
        }
