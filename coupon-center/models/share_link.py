"""Share link model."""
from datetime import datetime
from extensions import db


class ShareLink(db.Model):
    """ShareLink - shareable coupon claim links."""
    __tablename__ = 'share_links'

    id = db.Column(db.String(36), primary_key=True)
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=False)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    share_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    max_claims = db.Column(db.Integer, nullable=False)
    current_claims = db.Column(db.Integer, default=0)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'created_by': self.created_by,
            'share_code': self.share_code,
            'max_claims': self.max_claims,
            'current_claims': self.current_claims,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
