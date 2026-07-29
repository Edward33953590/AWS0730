"""Risk engine - AI-powered risk assessment with rule-based fallback."""
import uuid
import time
import json
from datetime import datetime
from collections import defaultdict
from models.risk_log import RiskLog
from models.blacklist import BlackWhiteList
from extensions import db


# In-memory request frequency tracker
# Format: {user_id: [(timestamp, action), ...]}
_request_history = defaultdict(list)

# Cleanup old entries threshold (keep last 60 seconds)
_HISTORY_WINDOW = 60


def _cleanup_history(user_id):
    """Remove old entries from request history."""
    cutoff = time.time() - _HISTORY_WINDOW
    _request_history[user_id] = [
        (ts, action) for ts, action in _request_history[user_id]
        if ts > cutoff
    ]


def _record_request(user_id, action):
    """Record a request for frequency tracking."""
    _request_history[user_id].append((time.time(), action))
    _cleanup_history(user_id)


def _get_request_count(user_id, seconds=10):
    """Get request count in the last N seconds."""
    cutoff = time.time() - seconds
    return sum(1 for ts, _ in _request_history[user_id] if ts > cutoff)


def check_risk(user_id, action='CLAIM', campaign_id=None):
    """
    Assess risk for a user action.
    Returns dict: {score, decision, reason, ai_explanation, source, rule_triggered}
    decision: ALLOW, BLOCK, REVIEW
    """
    # Record this request
    _record_request(user_id, action)

    # Step 1: Check blacklist/whitelist first
    bl_result = _check_blackwhitelist(user_id)
    if bl_result:
        _save_risk_log(user_id, action, bl_result)
        return bl_result

    # Step 2: Try AI risk assessment
    ai_result = _ai_risk_check(user_id, action, campaign_id)
    if ai_result:
        _save_risk_log(user_id, action, ai_result)
        return ai_result

    # Step 3: Fallback to rule engine
    rule_result = _rule_engine_check(user_id, action)
    _save_risk_log(user_id, action, rule_result)
    return rule_result


def _check_blackwhitelist(user_id):
    """Check if user is in blacklist or whitelist."""
    entry = BlackWhiteList.query.filter_by(user_id=user_id).first()
    if not entry:
        return None

    if entry.type == 'BLACK':
        return {
            'score': 100,
            'decision': 'BLOCK',
            'reason': f'用户在黑名单中: {entry.reason}',
            'ai_explanation': None,
            'source': 'blacklist',
            'rule_triggered': 'R-5',
        }
    elif entry.type == 'WHITE':
        return {
            'score': 0,
            'decision': 'ALLOW',
            'reason': '白名单用户，跳过风控',
            'ai_explanation': None,
            'source': 'whitelist',
            'rule_triggered': 'R-6',
        }
    return None


def _ai_risk_check(user_id, action, campaign_id):
    """Try AI-based risk assessment. Returns None if AI unavailable."""
    try:
        from services.bedrock_service import bedrock_service

        # Get user request stats
        count_10s = _get_request_count(user_id, 10)
        count_60s = _get_request_count(user_id, 60)

        prompt = f"""你是一个风控系统。请评估以下用户行为的风险等级。
用户行为数据:
- 用户ID: {user_id}
- 操作类型: {action}
- 最近10秒请求次数: {count_10s}
- 最近60秒请求次数: {count_60s}

请以JSON格式返回评估结果:
{{
  "score": 0-100的风险评分,
  "decision": "ALLOW"或"BLOCK"或"REVIEW",
  "reason": "简短的判断原因",
  "explanation": "详细的自然语言解释"
}}

评判标准:
- 10秒内超过50次请求: 高风险(BLOCK)
- 60秒内超过10次不同请求: 中风险(REVIEW)
- 正常行为: 低风险(ALLOW)"""

        result, error = bedrock_service.generate_json(prompt)
        if error:
            return None  # Fallback to rule engine

        if result and 'decision' in result:
            return {
                'score': int(result.get('score', 50)),
                'decision': result['decision'],
                'reason': result.get('reason', 'AI评估'),
                'ai_explanation': result.get('explanation', ''),
                'source': 'ai',
                'rule_triggered': None,
            }
        return None
    except Exception:
        return None  # Fallback to rule engine


def _rule_engine_check(user_id, action):
    """Rule-based risk assessment (fallback when AI unavailable)."""
    count_10s = _get_request_count(user_id, 10)
    count_60s = _get_request_count(user_id, 60)

    # R-1: High frequency (10s > 50)
    if count_10s >= 50:
        return {
            'score': 95,
            'decision': 'BLOCK',
            'reason': f'10秒内请求{count_10s}次，触发高频拦截规则',
            'ai_explanation': f'该用户在过去10秒内发起了{count_10s}次请求，远超正常使用频率，判定为异常刷券行为。',
            'source': 'rule_engine',
            'rule_triggered': 'R-1',
        }

    # R-2: Medium frequency (60s > 10 different claims)
    if count_60s >= 10:
        return {
            'score': 70,
            'decision': 'REVIEW',
            'reason': f'1分钟内请求{count_60s}次，需人工审核',
            'ai_explanation': f'该用户在1分钟内频繁操作{count_60s}次，行为模式异常，建议人工审核。',
            'source': 'rule_engine',
            'rule_triggered': 'R-2',
        }

    # R-3: New account rapid claims (check registration time)
    from models.user import User
    user = User.query.get(user_id)
    if user:
        minutes_since_register = (datetime.utcnow() - user.created_at).total_seconds() / 60
        if minutes_since_register < 5 and count_60s >= 3:
            return {
                'score': 65,
                'decision': 'REVIEW',
                'reason': '新注册账号短时间内频繁领券',
                'ai_explanation': f'该用户注册仅{minutes_since_register:.0f}分钟，已发起{count_60s}次领券请求，存在刷券嫌疑。',
                'source': 'rule_engine',
                'rule_triggered': 'R-3',
            }

    # Normal - ALLOW
    return {
        'score': 5,
        'decision': 'ALLOW',
        'reason': '正常行为',
        'ai_explanation': None,
        'source': 'rule_engine',
        'rule_triggered': None,
    }


def _save_risk_log(user_id, action, result):
    """Persist risk assessment result."""
    try:
        log = RiskLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            score=result['score'],
            decision=result['decision'],
            reason=result['reason'],
            rule_triggered=result.get('rule_triggered'),
            ai_explanation=result.get('ai_explanation'),
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()
