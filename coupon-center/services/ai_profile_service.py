"""AI user profile service - analyze user behavior and generate tags."""
from models.coupon import Coupon
from models.user import User


def get_user_profile(user_id):
    """
    Get AI-generated user profile with behavior tags.
    Returns: {tags: [...], summary, source}
    """
    user = User.query.get(user_id)
    if not user:
        return {'tags': [], 'summary': '用户不存在', 'source': 'error'}

    # Gather user data
    user_data = _collect_user_data(user_id)

    # Try AI profile
    ai_result = _ai_profile(user, user_data)
    if ai_result:
        return ai_result

    # Fallback to rule-based tags
    return _rule_based_profile(user, user_data)


def _collect_user_data(user_id):
    """Collect user behavior data for analysis."""
    coupons = Coupon.query.filter_by(user_id=user_id).all()

    total_claimed = len(coupons)
    redeemed = sum(1 for c in coupons if c.status == 'REDEEMED')
    expired = sum(1 for c in coupons if c.status == 'EXPIRED')

    # Type preferences
    type_counts = {}
    for c in coupons:
        if c.campaign:
            t = c.campaign.type
            type_counts[t] = type_counts.get(t, 0) + 1

    return {
        'total_claimed': total_claimed,
        'redeemed': redeemed,
        'expired': expired,
        'redeem_rate': round(redeemed / total_claimed, 2) if total_claimed > 0 else 0,
        'type_preferences': type_counts,
    }


def _ai_profile(user, user_data):
    """Try AI-based profile generation."""
    try:
        from services.bedrock_service import bedrock_service

        prompt = f"""你是一个用户行为分析专家。请根据以下用户数据生成用户画像。

用户名: {user.username}
注册时间: {user.created_at}
行为数据:
- 总领券数: {user_data['total_claimed']}
- 已核销: {user_data['redeemed']}
- 已过期: {user_data['expired']}
- 核销率: {user_data['redeem_rate']}
- 类型偏好: {user_data['type_preferences']}

请返回JSON格式:
{{
  "tags": ["标签1", "标签2", "标签3"],
  "summary": "50字以内的用户画像描述"
}}

标签示例: 价格敏感型、高频用户、低活跃用户、品类偏好-食品、满减偏好、新用户等"""

        result, error = bedrock_service.generate_json(prompt)
        if error or not result:
            return None

        if 'tags' in result:
            result['source'] = 'ai'
            return result
        return None

    except Exception:
        return None


def _rule_based_profile(user, user_data):
    """Generate profile using basic rules."""
    tags = []

    # Activity level
    if user_data['total_claimed'] >= 10:
        tags.append('高频用户')
    elif user_data['total_claimed'] >= 3:
        tags.append('普通活跃')
    else:
        tags.append('低活跃用户')

    # Redeem behavior
    if user_data['redeem_rate'] >= 0.8:
        tags.append('高核销率')
    elif user_data['redeem_rate'] <= 0.2 and user_data['total_claimed'] > 3:
        tags.append('囤券型')

    # Type preferences
    prefs = user_data['type_preferences']
    if prefs:
        top_type = max(prefs, key=prefs.get)
        type_names = {
            'FULL_REDUCTION': '满减偏好',
            'DISCOUNT': '折扣偏好',
            'NO_THRESHOLD': '无门槛偏好',
            'CATEGORY': '品类券偏好',
            'NEWCOMER': '新用户',
        }
        if top_type in type_names:
            tags.append(type_names[top_type])

    # Expired behavior
    if user_data['expired'] > user_data['redeemed']:
        tags.append('价格敏感型')

    summary = f"该用户共领取{user_data['total_claimed']}张券，核销率{int(user_data['redeem_rate']*100)}%。"

    return {'tags': tags, 'summary': summary, 'source': 'rule_based'}
