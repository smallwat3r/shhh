#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : serve.py
# Date  : 17.09.2019
# Author: matthieu petiteau <mpetiteau.pro@gmail.com>

"""General routes excluding blueprints."""
from flask import (redirect, render_template, request, send_from_directory,
                   url_for)

from . import app
from htmlmin.minify import html_minify as mn


@app.route('/')
def root():
    """Root."""
    return redirect(url_for('sender.create'))


@app.errorhandler(404)
def error_404(error):
    """404 not found."""
    return mn(render_template('not_found.html'))


@app.route('/robots.txt')
def static_from_root():
    """Robots.txt"""
    return send_from_directory(app.static_folder, request.path[1:])
