from datetime import datetime, timedelta
from celery_worker import celery
from extensions import db
from models import SessionRequest

@celery.task(name='tasks.close_stale_requests')
def close_stale_requests():
    limit = datetime.utcnow() - timedelta(days=7)
    requests = SessionRequest.query.filter(
        SessionRequest.status == 'PENDING',
        SessionRequest.requested_at <= limit
    ).all()

    for item in requests:
        item.status = 'REJECTED'
        item.decided_at = datetime.utcnow()

    db.session.commit()
    return {'closed': len(requests)}
