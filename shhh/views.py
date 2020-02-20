#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : views.py
# Date  : 17.09.2019
# Author: matthieu petiteau <mpetiteau.pro@gmail.com>

"""Flask views."""
from flask import render_template, request, send_from_directory

from . import app
from .utils.decorators import mandatory


@app.route("/")
def create():
    """Create secret."""
    return render_template("create.html")


@app.route("/c")
@mandatory(("link", "expires_on",))
def created():
    """Secret created."""
    context = {
        "link": request.args.get("link"),
        "expires_on": request.args.get("expires_on"),
    }
    return render_template("created.html", **context)


@app.route("/r/<slug>")
def read(slug):
    """Read secret."""
    return render_template("read.html", slug=slug)


@app.errorhandler(404)
def not_found(error):
    """404 not found."""
    return render_template("404.html", e=error)


@app.route("/robots.txt")
def robots():
    """Robots.txt"""
    return send_from_directory(app.static_folder, request.path[1:])
