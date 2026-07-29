"""Blacklist/Whitelist model."""
from datetime import datetime
from extensions import db


class BlackWhiteList(db.Model):
    """BlackWhiteList - user blacklist and whitelist management."""
    __tablename__ = 'black_white_list'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # BLACK or WHITE
    reason = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'type', name='uq_user_list_type'),
    )

    # Relationships
    target_user = db.relationship('User', foreign_keys=[user_id], backref='list_entries')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'reason': self.reason,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
