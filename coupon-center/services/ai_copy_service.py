"""AI copy generation service - marketing copy for campaigns."""
from services.campaign_service import CAMPAIGN_DEFAULTS


# Fallback templates when AI is unavailable
_FALLBACK_TEMPLATES = {
    'FULL_REDUCTION': {
        'title': '满{threshold}减{discount}，超值优惠',
        'description': '消费满{threshold}元立减{discount}元，让购物更划算！',
        'slogan': '满额立减，省钱无忧',
    },
    'DISCOUNT': {
        'title': '限时{rate}折优惠券',
        'description': '全场商品{rate}折优惠，机不可失！',
        'slogan': '低价畅购，折扣来袭',
    },
    'NO_THRESHOLD': {
        'title': '无门槛{discount}元现金券',
        'description': '无需凑单，直接减{discount}元，轻松享优惠！',
        'slogan': '无门槛，直接减',
    },
    'ADD_ON': {
        'title': '超值加购优惠',
        'description': '购买指定商品可低价加购精选好物！',
        'slogan': '加购更超值',
    },
    'CATEGORY': {
        'title': '{category}专区满{threshold}减{discount}',
        'description': '{category}品类精选，满{threshold}元减{discount}元！',
        'slogan': '品类精选，专属优惠',
    },
    'NEWCOMER': {
        'title': '新人专享{discount}元大礼',
        'description': '新用户注册即享{discount}元优惠，欢迎加入！',
        'slogan': '新人有礼，首单特惠',
    },
    'TIME_LIMITED': {
        'title': '限时特惠 {start_hour}:00-{end_hour}:00',
        'description': '每天{start_hour}点到{end_hour}点限时特惠，抓紧时间！',
        'slogan': '限时抢购，过时不候',
    },
}


def generate_copy(coupon_type, params, context=''):
    """
    Generate marketing copy for a campaign.
    Returns: {title, description, slogan, source}
    """
    # Try AI generation
    ai_result = _ai_generate(coupon_type, params, context)
    if ai_result:
        return ai_result

    # Fallback to templates
    return _fallback_generate(coupon_type, params)


def _ai_generate(coupon_type, params, context):
    """Try AI copy generation via Bedrock."""
    try:
        from services.bedrock_service import bedrock_service

        type_names = {
            'FULL_REDUCTION': '满减券',
            'DISCOUNT': '折扣券',
            'NO_THRESHOLD': '无门槛券',
            'ADD_ON': '加购券',
            'CATEGORY': '品类券',
            'NEWCOMER': '新人券',
            'TIME_LIMITED': '限时券',
        }

        prompt = f"""你是一个优秀的营销文案写手。请为以下优惠券活动生成吸引人的营销文案。

优惠券类型: {type_names.get(coupon_type, coupon_type)}
参数: {params}
{'活动场景: ' + context if context else ''}

请返回JSON格式:
{{
  "title": "活动标题（15字以内，吸引眼球）",
  "description": "活动描述（50字以内，清晰说明优惠内容）",
  "slogan": "营销口号（10字以内，朗朗上口）"
}}"""

        result, error = bedrock_service.generate_json(prompt)
        if error or not result:
            return None

        if 'title' in result and 'description' in result:
            result['source'] = 'ai'
            return result
        return None

    except Exception:
        return None


def _fallback_generate(coupon_type, params):
    """Generate copy from templates."""
    template = _FALLBACK_TEMPLATES.get(coupon_type, _FALLBACK_TEMPLATES['NO_THRESHOLD'])

    # Format with params
    format_params = {**params}
    if 'discount_rate' in format_params:
        format_params['rate'] = int(format_params['discount_rate'] * 10)

    try:
        title = template['title'].format(**format_params)
        description = template['description'].format(**format_params)
        slogan = template['slogan'].format(**format_params)
    except (KeyError, ValueError):
        title = template['title']
        description = template['description']
        slogan = template['slogan']

    return {
        'title': title,
        'description': description,
        'slogan': slogan,
        'source': 'fallback',
    }
