from datetime import datetime, timedelta

from shhh.domain import model
from shhh.extensions import db, scheduler
from shhh.scheduler import tasks


def test_scheduler_setup():
    jobs = scheduler.get_jobs()

    # check task name
    assert jobs[0].name == "delete_expired_records"

    # check that the task will run before the next minute
    scheduled = jobs[0].next_run_time.strftime("%Y-%m-%d %H:%M:%S")
    next_minute = (datetime.now() +
                   timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
    assert scheduled <= next_minute


def test_scheduler_job():
    # pause the scheduler so we can trigger it on demand
    scheduler.pause_job("delete_expired_records")

    # create multiple expired secrets
    expired_ids = []
    for i in range(5):
        secret = model.Secret.encrypt(message=f"secret {i}",
                                      passphrase="Hello123",
                                      expire_code="1d",
                                      tries=3)
        secret.date_expires = datetime.now() - timedelta(days=1)
        db.session.add(secret)
        expired_ids.append(secret.external_id)

    # create a non-expired secret that should NOT be deleted
    active_secret = model.Secret.encrypt(message="active",
                                         passphrase="Hello123",
                                         expire_code="1d",
                                         tries=3)
    db.session.add(active_secret)
    db.session.commit()

    active_id = active_secret.external_id

    # run scheduler task
    tasks.delete_expired_records()

    # all expired secrets should have been deleted
    for external_id in expired_ids:
        secret = db.session.query(model.Secret).filter(
            model.Secret.has_external_id(external_id)).one_or_none()
        assert secret is None

    # the active secret should still exist
    active = db.session.query(model.Secret).filter(
        model.Secret.has_external_id(active_id)).one_or_none()
    assert active is not None
