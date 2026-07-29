"""Campaign service - business logic for campaign management."""
import uuid
import json
from datetime import datetime
from models.campaign import Campaign
from extensions import db


# Default params for each coupon type
CAMPAIGN_DEFAULTS = {
    'FULL_REDUCTION': {'threshold': 100, 'discount': 20},
    'DISCOUNT': {'discount_rate': 0.8},
    'NO_THRESHOLD': {'discount': 5},
    'ADD_ON': {'main_product': '', 'add_product': '', 'add_price': 1},
    'CATEGORY': {'category': '', 'threshold': 50, 'discount': 10},
    'NEWCOMER': {'discount': 15},
    'TIME_LIMITED': {'start_hour': 11, 'end_hour': 13, 'discount': 8},
}

VALID_TYPES = list(CAMPAIGN_DEFAULTS.keys())


def get_default_params(coupon_type):
    """Get default parameters for a coupon type."""
    return CAMPAIGN_DEFAULTS.get(coupon_type, {})


def validate_campaign_data(data, is_update=False):
    """Validate campaign creation/update data. Returns (cleaned_data, error_message)."""
    errors = []

    if not is_update:
        if not data.get('name'):
            errors.append('活动名称不能为空')
        if not data.get('type') or data['type'] not in VALID_TYPES:
            errors.append(f'无效的优惠券类型，可 {", ".join(VALID_TYPES)}')
        if not data.get('total_stock') or int(data.get('total_stock', 0)) <= 0:
            errors.append('库存数量必须大于0')

    if errors:
        return None, '; '.join(errors)

    return data, None


def create_campaign(data, operator_id):
    """Create a new campaign."""
    coupon_type = data['type']
    default_params = get_default_params(coupon_type)

    # Merge user params with defaults
    user_params = data.get('params', {})
    params = {**default_params, **user_params}

    total_stock = int(data.get('total_stock', 100))

    campaign = Campaign(
        id=str(uuid.uuid4()),
        name=data['name'],
        description=data.get('description', ''),
        type=coupon_type,
        params_json=json.dumps(params, ensure_ascii=False),
        total_stock=total_stock,
        remaining_stock=total_stock,
        limit_per_user=int(data.get('limit_per_user', 1)),
        validity_mode=data.get('validity_mode', 'RELATIVE'),
        validity_days=int(data['validity_days']) if data.get('validity_days') else 1,
        fixed_start_date=_parse_datetime(data.get('fixed_start_date')),
        fixed_end_date=_parse_datetime(data.get('fixed_end_date')),
        start_time=_parse_datetime(data.get('start_time')),
        transferable=bool(data.get('transferable', False)),
        stackable=bool(data.get('stackable', False)),
        shareable=bool(data.get('shareable', False)),
        share_limit=int(data.get('share_limit', 3)),
        template_id=data.get('template_id'),
        created_by=operator_id,
    )

    db.session.add(campaign)
    db.session.commit()
    return campaign


def update_campaign(campaign_id, data):
    """Update an existing campaign."""
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return None, '活动不存在'

    # Update allowed fields
    if 'name' in data:
        campaign.name = data['name']
    if 'description' in data:
        campaign.description = data['description']
    if 'params' in data:
        campaign.params = data['params']
    if 'limit_per_user' in data:
        campaign.limit_per_user = int(data['limit_per_user'])
    if 'validity_mode' in data:
        campaign.validity_mode = data['validity_mode']
    if 'validity_days' in data:
        campaign.validity_days = int(data['validity_days']) if data['validity_days'] else None
    if 'fixed_start_date' in data:
        campaign.fixed_start_date = _parse_datetime(data['fixed_start_date'])
    if 'fixed_end_date' in data:
        campaign.fixed_end_date = _parse_datetime(data['fixed_end_date'])
    if 'start_time' in data:
        campaign.start_time = _parse_datetime(data['start_time'])
    if 'transferable' in data:
        campaign.transferable = bool(data['transferable'])
    if 'stackable' in data:
        campaign.stackable = bool(data['stackable'])
    if 'shareable' in data:
        campaign.shareable = bool(data['shareable'])
    if 'share_limit' in data:
        campaign.share_limit = int(data['share_limit'])

    # Stock can only be increased
    if 'total_stock' in data:
        new_stock = int(data['total_stock'])
        claimed = campaign.total_stock - campaign.remaining_stock
        if new_stock < claimed:
            return None, f'库存不能低于已发放数 {claimed})'
        stock_diff = new_stock - campaign.total_stock
        campaign.total_stock = new_stock
        campaign.remaining_stock += stock_diff

    campaign.updated_at = datetime.utcnow()
    db.session.commit()
    return campaign, None


def delete_campaign(campaign_id):
    """Delete a campaign (only if no coupons issued)."""
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return False, '活动不存在'

    claimed = campaign.total_stock - campaign.remaining_stock
    if claimed > 0:
        return False, '已有用户领取，无法删除'

    db.session.delete(campaign)
    db.session.commit()
    return True, None


def list_campaigns(page=1, page_size=20, coupon_type=None, active_only=False):
    """List campaigns with pagination and filters."""
    query = Campaign.query

    if coupon_type:
        query = query.filter_by(type=coupon_type)

    if active_only:
        query = query.filter(Campaign.remaining_stock > 0)

    query = query.order_by(Campaign.created_at.desc())
    total = query.count()

    campaigns = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        'items': [c.to_dict() for c in campaigns],
        'total': total,
        'page': page,
        'page_size': page_size,
    }


def _parse_datetime(value):
    """Parse datetime string to datetime object."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None
