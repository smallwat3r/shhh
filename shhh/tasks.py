#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : tasks.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 12.01.2020

"""Celery tasks management."""
from . import celery, utils
from celery.schedules import crontab


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Register task to run periodically."""
    sender.add_periodic_task(crontab(minute="*/5"), delete_expired_links.s())


@celery.task
def delete_expired_links():
    """Delete expired links from the database."""
    utils.delete_expired_links()
