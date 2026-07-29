"""Operation log model."""
from datetime import datetime
from extensions import db


class OperationLog(db.Model):
    """OperationLog - audit trail for all key operations."""
    __tablename__ = 'operation_logs'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    target = db.Column(db.String(100), nullable=True)
    detail = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_oplog_user', 'user_id'),
        db.Index('idx_oplog_action', 'action'),
        db.Index('idx_oplog_time', 'created_at'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'target': self.target,
            'detail': self.detail,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
