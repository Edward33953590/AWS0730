"""Notification model."""
from datetime import datetime
from extensions import db


class Notification(db.Model):
    """Notification - in-app notifications for users."""
    __tablename__ = 'notifications'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(30), nullable=False)
    content = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_notification_user_read', 'user_id', 'read'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'content': self.content,
            'read': self.read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
