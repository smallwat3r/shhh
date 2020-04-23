#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : tasks.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 12.01.2020
"""Celery tasks management."""
from celery.schedules import crontab

from .. import celery
from ..utils import database


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Register task to run periodically."""
    # Trigger Celery beat to delete records every minutes.
    sender.add_periodic_task(crontab(minute="*/1"), delete_expired_links.s())


@celery.task
def delete_expired_links():
    """Delete expired links from the database."""
    with database.DbConn() as db:
        db.commit("delete_expired_links.sql")
