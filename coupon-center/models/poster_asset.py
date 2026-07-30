"""Poster asset model - background images for coupon poster generation."""
import json
from datetime import datetime
from extensions import db


class PosterAsset(db.Model):
    """Poster asset table - stores background image metadata for poster generation."""
    __tablename__ = 'poster_assets'

    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    filename = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), default='')
    style = db.Column(db.String(30), default='')
    # Text overlay area: JSON with {x, y, width, height}
    text_area_json = db.Column(db.Text, nullable=False, default='{}')
    # Recommended text color (hex)
    text_color = db.Column(db.String(20), default='#ffffff')
    # Recommended font size
    recommended_font_size = db.Column(db.Integer, default=28)
    # Whether this asset is active/available
    is_active = db.Column(db.Boolean, default=True)
    # Upload info
    uploaded_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def text_area(self):
        return json.loads(self.text_area_json) if self.text_area_json else {}

    @text_area.setter
    def text_area(self, value):
        self.text_area_json = json.dumps(value, ensure_ascii=False)

    @property
    def image_url(self):
        return f'/static/poster_assets/{self.filename}'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'filename': self.filename,
            'category': self.category,
            'style': self.style,
            'text_area': self.text_area,
            'text_color': self.text_color,
            'recommended_font_size': self.recommended_font_size,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
