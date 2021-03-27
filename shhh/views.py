import gzip
from io import BytesIO

from flask import current_app as app
from flask import redirect
from flask import render_template as rt
from flask import request, send_from_directory, url_for
from htmlmin.main import minify

from . import __version__


@app.route("/")
def create():
    """View to create a secret."""
    return rt("create.html")


@app.route("/c")
def created():
    """View to see the link for the created secret."""
    link, expires_on = request.args.get("link"), request.args.get("expires_on")
    if not link or not expires_on:
        return redirect(url_for("create"))
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


@app.context_processor
def context():
    """Context data."""
    return {"version": __version__}


@app.after_request
def response_handler(response):
    """Minify HTML and use gzip compression."""
    if response.mimetype == "text/html":
        response.set_data(minify(response.get_data(as_text=True)))

    # Do not gzip below 500 bytes or on JSON content
    if response.content_length < 500 or response.mimetype == "application/json":
        return response

    response.direct_passthrough = False

    gzip_buffer = BytesIO()
    gzip_file = gzip.GzipFile(mode="wb", compresslevel=6, fileobj=gzip_buffer)
    gzip_file.write(response.get_data())
    gzip_file.close()

    response.set_data(gzip_buffer.getvalue())
    response.headers.add("Content-Encoding", "gzip")
    return response
