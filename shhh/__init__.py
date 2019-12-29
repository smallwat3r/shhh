#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : __init__.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 17.09.2019

'''Init application.'''
import os

from flask import Flask

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

# Load Flask configuration from Class.
configurations = {
    'development': 'shhh.config.DefaultConfig',
    'production': 'shhh.config.ProductionConfig'
}
app.config.from_object(configurations[os.getenv('FLASK_ENV')])

from shhh import views
