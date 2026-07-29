"""Operation log service - audit trail for key actions."""
import uuid
import json
from datetime import datetime
from models.operation_log import OperationLog
from extensions import db


def log_operation(user_id, action, target=None, detail=None):
    """Record an operation log entry. Non-blocking (best effort)."""
    try:
        detail_str = json.dumps(detail, ensure_ascii=False) if isinstance(detail, dict) else detail
        log = OperationLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            target=target,
            detail=detail_str,
            created_at=datetime.utcnow(),
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()


def get_logs(page=1, page_size=50, action=None, user_id=None, date_from=None, date_to=None):
    """Query operation logs with filters."""
    query = OperationLog.query

    if action:
        query = query.filter_by(action=action)
    if user_id:
        query = query.filter_by(user_id=user_id)
    if date_from:
        query = query.filter(OperationLog.created_at >= date_from)
    if date_to:
        query = query.filter(OperationLog.created_at <= date_to)

    query = query.order_by(OperationLog.created_at.desc())
    total = query.count()
    logs = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        'items': [log.to_dict() for log in logs],
        'total': total,
        'page': page,
        'page_size': page_size,
    }
