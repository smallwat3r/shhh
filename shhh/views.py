from flask import (
    render_template, request, send_from_directory, redirect, url_for,
    current_app as app
)


@app.route("/")
def create():
    """Create secret."""
    return render_template("create.html")


@app.route("/c")
def created():
    """Secret created."""
    link, expires_on = request.args.get("link"), request.args.get("expires_on")
    if link and expires_on:
        return render_template("created.html", link=link, expires_on=expires_on)
    return redirect(url_for("create"))


@app.route("/r/<slug>")
def read(slug):
    """Read secret."""
    return render_template("read.html", slug=slug)


@app.errorhandler(404)
def not_found(error):
    """404 not found."""
    return render_template("404.html", error=error)


@app.route("/robots.txt")
def robots():
    """Robots.txt"""
    return send_from_directory(app.static_folder, request.path[1:])
