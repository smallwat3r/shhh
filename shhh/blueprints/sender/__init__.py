#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : __init__.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 17.09.2019

"""Init sender blueprint."""
import os

from flask import Blueprint

sender = Blueprint('sender', __name__, template_folder='pages')
DIR_PATH = os.path.dirname(os.path.abspath(__file__))

from ... import serve
from .sender_post import *
