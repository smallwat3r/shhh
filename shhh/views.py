import inspect

from flask import current_app as app
from flask import redirect
from flask import render_template as rt
from flask import request, send_from_directory, url_for


def qs_to_args(f):
    """Querystring to Args.

    Decorator function to parse mandatory parameters in function args from
    querystring. Check that the query keys are matching the args.

    """

    def wrapper(*args, **kwargs):
        if sorted(inspect.getargspec(f).args) != sorted(request.args.keys()):
            return redirect(url_for("create"))
        return f(**request.args)

    return wrapper


@app.route("/")
def create():
    """View to create a secret."""
    return rt("create.html")


@app.route("/c")
@qs_to_args
def created(link, expires_on):
    """View to see the link for the created secret."""
    return rt("created.html", **locals())


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
