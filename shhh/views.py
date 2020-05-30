import inspect

from flask import current_app as app
from flask import redirect
from flask import render_template as rt
from flask import request, send_from_directory, url_for

from htmlmin.main import minify


def qs_to_args(f):
    """Querystring to Args.

    Decorator function to parse mandatory parameters in function args from
    querystring. Check that the query keys are matching the args.

    """

    def wrapper(*args, **kwargs):

        if sorted(inspect.getfullargspec(f).args) != sorted(
                request.args.keys()):
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
    return rt("created.html", link=link, expires_on=expires_on)


@app.route("/r/<slug>")
def read(slug):
    """View to read a secret."""
    return rt("read.html", slug=slug)


@app.errorhandler(404)
def not_found(error):
    """404 handler."""
    return rt("404.html", error=error), 404


@app.route("/robots.txt")
def robots():
    """Robots handler."""
    return send_from_directory(app.static_folder, request.path[1:])


@app.after_request
def html_minify(response):
    """Minimise html responses."""
    if response.content_type == u"text/html; charset=utf-8":
        response.set_data(minify(response.get_data(as_text=True)))
    return response
