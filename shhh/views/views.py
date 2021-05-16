from flask import current_app as app
from flask import Blueprint, redirect
from flask import render_template as rt
from flask import request, url_for, send_from_directory

views = Blueprint("views", __name__, url_prefix="/")


@views.get("/")
def create():
    """View to create a secret."""
    return rt("create.html", secret_max_length=app.config["SHHH_SECRET_MAX_LENGTH"])


@views.get("/secret")
def created():
    """View to see the link for the created secret."""
    link, expires_on = request.args.get("link"), request.args.get("expires_on")
    if not link or not expires_on:
        return redirect(url_for("views.create"))
    return rt("created.html", link=link, expires_on=expires_on)


@views.get("/secret/<slug>")
def read(slug):
    """View to read a secret."""
    return rt("read.html", slug=slug)


@views.get("/robots.txt")
def robots():
    """Serve robots.txt file."""
    return send_from_directory(app.static_folder, request.path[1:])
