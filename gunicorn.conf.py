#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : gunicorn.conf.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 14.01.2020

"""Gunicorn configuration file"""
import multiprocessing

bind = "0.0.0.0:5000"
worker_class = "gevent"
workers = multiprocessing.cpu_count() * 2 + 1
