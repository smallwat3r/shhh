from datetime import datetime, timedelta

from shhh.domain import model
from shhh.extensions import db, scheduler
from shhh.scheduler import tasks


def test_scheduler_setup():
    jobs = scheduler.get_jobs()

    # check task name
    assert jobs[0].name == "delete_expired_links"

    # check that the task will run before the next minute
    scheduled = jobs[0].next_run_time.strftime("%Y-%m-%d %H:%M:%S")
    next_minute = (datetime.now() +
                   timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
    assert scheduled <= next_minute


def test_scheduler_job():
    # pause the scheduler so we can trigger it on demand
    scheduler.pause_job("delete_expired_links")

    # create a secret, and make it outdated
    secret = model.Secret.encrypt(message="hello",
                                  passphrase="Hello123",
                                  expire_code="1d",
                                  tries=3)
    secret.date_expires = datetime.now() - timedelta(days=1)
    db.session.add(secret)
    db.session.commit()

    external_id = secret.external_id

    # run scheduler task
    tasks.delete_expired_links()

    secret = db.session.query(model.Secret).filter(
        model.Secret.has_external_id(external_id)).one_or_none()

    # the secret should have been deleted
    assert secret is None
