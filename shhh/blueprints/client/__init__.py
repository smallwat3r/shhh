#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : __init__.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 17.09.2019

"""Init client (reader) blueprint. """
import os

from flask import Blueprint

client = Blueprint('client', __name__, template_folder='pages')
DIR_PATH = os.path.dirname(os.path.abspath(__file__))

from ... import serve
from .client_read import *
