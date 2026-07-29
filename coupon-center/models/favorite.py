"""Favorite model."""
from datetime import datetime
from extensions import db


class Favorite(db.Model):
    """Favorite - user campaign bookmarks."""
    __tablename__ = 'favorites'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'campaign_id', name='uq_user_campaign_fav'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'campaign_id': self.campaign_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
