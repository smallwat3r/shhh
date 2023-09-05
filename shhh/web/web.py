from flask import Blueprint
from flask import current_app as app
from flask import redirect
from flask import render_template as rt
from flask import request, send_from_directory, url_for

from shhh.constants import (DEFAULT_EXPIRATION_TIME_VALUE,
                            DEFAULT_READ_TRIES_VALUE,
                            READ_TRIES_VALUES,
                            EXPIRATION_TIME_VALUES)

web = Blueprint("web", __name__, url_prefix="/")


@web.get("/")
def create():
    return rt("create.html",
              secret_max_length=app.config["SHHH_SECRET_MAX_LENGTH"],
              expiration_time_values=EXPIRATION_TIME_VALUES,
              default_expiration_time_value=DEFAULT_EXPIRATION_TIME_VALUE,
              read_tries_values=READ_TRIES_VALUES,
              default_read_tries_value=DEFAULT_READ_TRIES_VALUE)


@web.get("/secret")
def created():
    link, expires_on = request.args.get("link"), request.args.get("expires_on")
    if not link or not expires_on:
        return redirect(url_for("web.create"))
    return rt("created.html", link=link, expires_on=expires_on)


@web.get("/secret/<external_id>")
def read(external_id: int):
    return rt("read.html", external_id=external_id)


@web.get("/robots.txt")
def robots_dot_txt():
    return send_from_directory(app.static_folder, request.path[1:])
