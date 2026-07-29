"""Campaign model."""
import json
from datetime import datetime
from extensions import db


class Campaign(db.Model):
    """Campaign table - coupon activities created by operators."""
    __tablename__ = 'campaigns'

    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    type = db.Column(db.String(30), nullable=False)
    # FULL_REDUCTION, DISCOUNT, NO_THRESHOLD, ADD_ON, CATEGORY, NEWCOMER, TIME_LIMITED
    params_json = db.Column(db.Text, nullable=False, default='{}')
    total_stock = db.Column(db.Integer, nullable=False)
    remaining_stock = db.Column(db.Integer, nullable=False)
    limit_per_user = db.Column(db.Integer, nullable=False, default=1)
    validity_mode = db.Column(db.String(20), nullable=False, default='RELATIVE')
    # RELATIVE (N days after claim) or FIXED (fixed date range)
    validity_days = db.Column(db.Integer, default=1)
    fixed_start_date = db.Column(db.DateTime, nullable=True)
    fixed_end_date = db.Column(db.DateTime, nullable=True)
    start_time = db.Column(db.DateTime, nullable=True)  # Activity open time
    transferable = db.Column(db.Boolean, default=False)
    stackable = db.Column(db.Boolean, default=False)
    shareable = db.Column(db.Boolean, default=False)
    share_limit = db.Column(db.Integer, default=3)
    template_id = db.Column(db.String(36), nullable=True)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    coupons = db.relationship('Coupon', backref='campaign', lazy='dynamic')

    @property
    def params(self):
        return json.loads(self.params_json) if self.params_json else {}

    @params.setter
    def params(self, value):
        self.params_json = json.dumps(value, ensure_ascii=False)

    @property
    def claimed_count(self):
        return self.total_stock - self.remaining_stock

    @property
    def claim_percentage(self):
        if self.total_stock == 0:
            return 0
        return round((self.claimed_count / self.total_stock) * 100)

    @property
    def is_active(self):
        now = datetime.utcnow()
        if self.start_time and now < self.start_time:
            return False
        if self.remaining_stock <= 0:
            return False
        return True

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'params': self.params,
            'total_stock': self.total_stock,
            'remaining_stock': self.remaining_stock,
            'limit_per_user': self.limit_per_user,
            'validity_mode': self.validity_mode,
            'validity_days': self.validity_days,
            'fixed_start_date': self.fixed_start_date.isoformat() if self.fixed_start_date else None,
            'fixed_end_date': self.fixed_end_date.isoformat() if self.fixed_end_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'transferable': self.transferable,
            'stackable': self.stackable,
            'shareable': self.shareable,
            'share_limit': self.share_limit,
            'claim_percentage': self.claim_percentage,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
