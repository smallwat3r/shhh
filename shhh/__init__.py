#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : __init__.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 17.09.2019

"""Init application."""
import os

from flask import Flask
from werkzeug.contrib.fixers import ProxyFix

from flask_static_compress import FlaskStaticCompress

__all__ = []

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(ROOT_PATH, 'front/shared_templates')

app = Flask(__name__,
            template_folder=TEMPLATES,
            static_folder='front/static')

compress = FlaskStaticCompress(app)
app.wsgi_app = ProxyFix(app.wsgi_app)


# Load Flask configuration from Class. ---------------------------------------
configurations = {
        'development': 'shhh.config.DefaultConfig',
        'production': 'shhh.config.ProductionConfig'

}
app.config.from_object(configurations[os.getenv('FLASK_ENV')])


# Blueprints. ----------------------------------------------------------------
from .blueprints.client import *
from .blueprints.sender import *

app.register_blueprint(sender)
app.register_blueprint(client)
