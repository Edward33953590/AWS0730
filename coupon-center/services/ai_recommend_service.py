"""AI recommendation service - personalized coupon recommendations."""
from models.campaign import Campaign
from models.coupon import Coupon


def get_recommendations(user_id):
    """
    Get personalized coupon recommendations for a user.
    Uses AI when available, falls back to popular coupons.
    Returns: {recommendations: [...], source: 'ai'|'fallback'}
    """
    # Get user history for context
    user_history = _get_user_history(user_id)
    available_campaigns = _get_available_campaigns(user_id)

    if not available_campaigns:
        return {'recommendations': [], 'source': 'fallback'}

    # Try AI recommendation
    ai_result = _ai_recommend(user_history, available_campaigns)
    if ai_result:
        return ai_result

    # Fallback: popular campaigns sorted by claim count
    return _fallback_recommend(available_campaigns)


def _get_user_history(user_id):
    """Get user's coupon claiming history for AI context."""
    coupons = Coupon.query.filter_by(user_id=user_id).limit(20).all()
    history = []
    for c in coupons:
        if c.campaign:
            history.append({
                'campaign_type': c.campaign.type,
                'campaign_name': c.campaign.name,
                'status': c.status,
            })
    return history


def _get_available_campaigns(user_id):
    """Get campaigns that the user can still claim."""
    campaigns = Campaign.query.filter(Campaign.remaining_stock > 0).all()
    available = []
    for camp in campaigns:
        # Check if user already at limit
        claimed = Coupon.query.filter_by(
            campaign_id=camp.id, user_id=user_id
        ).filter(Coupon.status != 'TRANSFERRED').count()
        if claimed < camp.limit_per_user:
            available.append(camp)
    return available


def _ai_recommend(user_history, available_campaigns):
    """Try AI-based recommendation."""
    try:
        from services.bedrock_service import bedrock_service

        # Build prompt
        history_text = ""
        if user_history:
            history_text = "用户历史领券记录:\n"
            for h in user_history[:10]:
                history_text += f"- {h['campaign_name']} (类型:{h['campaign_type']}, 状态:{h['status']})\n"
        else:
            history_text = "该用户暂无历史记录（新用户）。\n"

        campaigns_text = "当前可用优惠券活动:\n"
        for i, c in enumerate(available_campaigns[:15]):
            campaigns_text += f"{i+1}. {c.name} (类型:{c.type}, 参数:{c.params}, 剩余:{c.remaining_stock})\n"

        prompt = f"""你是一个智能优惠券推荐系统。请根据用户的历史行为，从可用活动中推荐最适合的优惠券。

{history_text}
{campaigns_text}

请返回JSON格式的推荐列表（推荐3-5个），每个推荐包含:
- index: 活动编号（从1开始）
- reason: 推荐理由（简短自然语言，50字以内）
- score: 推荐匹配度（0-1）

格式:
{{"recommendations": [{{"index": 1, "reason": "...", "score": 0.95}}]}}"""

        result, error = bedrock_service.generate_json(prompt)
        if error or not result:
            return None

        recs = result.get('recommendations', [])
        if not recs:
            return None

        # Map indices back to campaigns
        output = []
        for rec in recs[:5]:
            idx = rec.get('index', 1) - 1
            if 0 <= idx < len(available_campaigns):
                camp = available_campaigns[idx]
                output.append({
                    'campaign_id': camp.id,
                    'campaign_name': camp.name,
                    'campaign_type': camp.type,
                    'params': camp.params,
                    'remaining_stock': camp.remaining_stock,
                    'reason': rec.get('reason', '为您精选推荐'),
                    'score': rec.get('score', 0.8),
                })

        if output:
            return {'recommendations': output, 'source': 'ai'}
        return None

    except Exception:
        return None


def _fallback_recommend(available_campaigns):
    """Fallback: recommend by popularity (most claimed first)."""
    sorted_campaigns = sorted(
        available_campaigns,
        key=lambda c: c.total_stock - c.remaining_stock,
        reverse=True
    )

    recommendations = []
    for camp in sorted_campaigns[:5]:
        recommendations.append({
            'campaign_id': camp.id,
            'campaign_name': camp.name,
            'campaign_type': camp.type,
            'params': camp.params,
            'remaining_stock': camp.remaining_stock,
            'reason': '热门优惠券推荐',
            'score': 0.7,
        })

    return {'recommendations': recommendations, 'source': 'fallback'}
