"""Campaign template model."""
import json
from datetime import datetime
from extensions import db


class CampaignTemplate(db.Model):
    """CampaignTemplate - reusable campaign configurations."""
    __tablename__ = 'campaign_templates'

    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    config_json = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def config(self):
        return json.loads(self.config_json) if self.config_json else {}

    @config.setter
    def config(self, value):
        self.config_json = json.dumps(value, ensure_ascii=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'config': self.config,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
