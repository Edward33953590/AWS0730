"""Stats service - aggregate data for admin dashboard."""
from datetime import datetime, timedelta
from models.campaign import Campaign
from models.coupon import Coupon
from models.redemption import Redemption
from models.user import User
from models.risk_log import RiskLog
from extensions import db


def get_overview():
    """Get overview statistics."""
    total_campaigns = Campaign.query.count()
    total_coupons = Coupon.query.count()
    total_redeemed = Coupon.query.filter_by(status='REDEEMED').count()
    total_users = User.query.count()
    risk_blocks = RiskLog.query.filter_by(decision='BLOCK').count()

    claim_rate = round(total_coupons / max(sum(c.total_stock for c in Campaign.query.all()), 1), 2)
    redeem_rate = round(total_redeemed / max(total_coupons, 1), 2)

    # Daily claims for last 7 days
    daily_claims = []
    for i in range(6, -1, -1):
        day = datetime.utcnow().date() - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = day_start + timedelta(days=1)
        count = Coupon.query.filter(
            Coupon.claimed_at >= day_start,
            Coupon.claimed_at < day_end
        ).count()
        daily_claims.append({'date': day.isoformat(), 'count': count})

    # Type distribution
    type_dist = db.session.query(
        Campaign.type, db.func.count(Campaign.id)
    ).group_by(Campaign.type).all()
    type_distribution = [{'type': t, 'count': c} for t, c in type_dist]

    return {
        'total_campaigns': total_campaigns,
        'total_coupons': total_coupons,
        'total_redeemed': total_redeemed,
        'total_users': total_users,
        'risk_blocks': risk_blocks,
        'claim_rate': claim_rate,
        'redeem_rate': redeem_rate,
        'daily_claims': daily_claims,
        'type_distribution': type_distribution,
    }
