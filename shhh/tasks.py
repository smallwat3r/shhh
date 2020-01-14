#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : tasks.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 12.01.2020

"""Celery tasks management."""
from . import celery, database, logger
from celery.schedules import crontab


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Register task to run periodically."""
    sender.add_periodic_task(crontab(minute="*/1"), delete_expired_links.s())


@celery.task
def delete_expired_links():
    """Delete expired links from the database."""
    with database.DbConn() as db:
        db.commit("delete_expired_links.sql")

    logger.info("celery ran to check and delete expired records")
