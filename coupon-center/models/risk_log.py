"""Risk log model."""
from datetime import datetime
from extensions import db


class RiskLog(db.Model):
    """RiskLog - records risk assessment results."""
    __tablename__ = 'risk_logs'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(30), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    decision = db.Column(db.String(20), nullable=False)  # ALLOW, BLOCK, REVIEW
    reason = db.Column(db.Text, nullable=False)
    rule_triggered = db.Column(db.String(20), nullable=True)
    ai_explanation = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_risk_user', 'user_id'),
        db.Index('idx_risk_decision', 'decision'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'score': self.score,
            'decision': self.decision,
            'reason': self.reason,
            'rule_triggered': self.rule_triggered,
            'ai_explanation': self.ai_explanation,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
