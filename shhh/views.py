#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : views.py
# Date  : 17.09.2019
# Author: matthieu petiteau <mpetiteau.pro@gmail.com>

"""Flask views."""
import ast

from flask import (
    jsonify, redirect, render_template, request, send_from_directory, url_for
)

from . import app, utils
from .decorators import check_arg, need_arg, on_post


@app.route("/")
def index():
    return redirect(url_for("create"))


@app.route("/c", methods=["GET", "POST"])
@check_arg("data")
def create():
    """Create secret."""

    @on_post(("inputSecret", "passPhrase", "expiresValue",))
    def _generate():
        """Generate secret link."""
        slug, expires = utils.generate_link(
            secret=request.form.get("inputSecret"),
            passphrase=request.form.get("passPhrase"),
            expires=request.form.get("expiresValue"),
        )
        return {
            "link": f"{request.url_root}r/{slug}",
            "expires": str(expires.strftime("%Y-%m-%d at %H:%M")),
        }

    def data():
        if request.args.get("data"):
            return ast.literal_eval(request.args.get("data"))

    if request.method == "POST":
        return redirect(url_for("create", data=_generate()))

    return render_template("create.html", data=data())


@app.route("/r/<slug>")
def read(slug):
    """Read secret."""
    return render_template("read.html", slug=slug)


@app.route("/api/r")
@need_arg(("slug", "passphrase",))
def api_read():
    """Read secret, API call."""
    return jsonify(
        utils.decrypt(
            slug=request.args.get("slug"), passphrase=request.args.get("passphrase")
        )
    )


@app.errorhandler(404)
def error_404(error):
    """404 not found."""
    return render_template("404.html", e=error)


@app.route("/robots.txt")
def static_from_root():
    """Robots.txt"""
    return send_from_directory(app.static_folder, request.path[1:])
