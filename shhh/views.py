from functools import wraps

from flask import current_app as app
from flask import redirect
from flask import render_template as rt
from flask import request, send_from_directory, url_for


def need(params):
    """Needed params to access page."""
    def inner(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            for param in params:
                if not request.args.get(param):
                    return redirect(url_for("create"))
            return f(*args, **kwargs)
        return wrapper
    return inner


@app.route("/")
def create():
    """View to create a secret."""
    return rt("create.html")


@app.route("/c")
@need(("link", "expires_on", ))
def created():
    """View to see the link for the created secret."""
    return rt("created.html",
              link=request.args.get("link"),
              expires_on=request.args.get("expires_on"))


@app.route("/r/<slug>")
def read(slug):
    """View to read a secret."""
    return rt("read.html", slug=slug)


@app.errorhandler(404)
def not_found(error):
    """404 handler."""
    return rt("404.html", error=error)


@app.route("/robots.txt")
def robots():
    """Robots handler."""
    return send_from_directory(app.static_folder, request.path[1:])
