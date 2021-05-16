import gzip
import logging
from enum import Enum
from http import HTTPStatus
from io import BytesIO

from apscheduler.schedulers import SchedulerAlreadyRunningError
from flask import Flask
from flask import render_template as rt
from flask_assets import Bundle
from htmlmin.main import minify
from webassets.env import RegisterError

from shhh import __version__
from shhh.api import api
from shhh.extensions import assets, db, scheduler
from shhh.views import views


class EnvConfig(Enum):
    """Environment config values."""

    TESTING = "testing"
    DEV_LOCAL = "dev-local"
    DEV_DOCKER = "dev-docker"
    HEROKU = "heroku"
    PRODUCTION = "production"


def create_app(env):
    """Application factory."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [sev %(levelno)s] [%(levelname)s] [%(name)s]> %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
    )

    if env == EnvConfig.TESTING.value:
        logging.getLogger("shhh").setLevel(logging.CRITICAL)
        logging.getLogger("apscheduler").setLevel(logging.CRITICAL)
        logging.getLogger("tasks").setLevel(logging.CRITICAL)

    app = Flask(__name__)

    configurations = {
        EnvConfig.TESTING.value: "shhh.config.TestConfig",
        EnvConfig.DEV_LOCAL.value: "shhh.config.DefaultConfig",
        EnvConfig.DEV_DOCKER.value: "shhh.config.DockerConfig",
        EnvConfig.HEROKU.value: "shhh.config.HerokuConfig",
        EnvConfig.PRODUCTION.value: "shhh.config.ProductionConfig",
    }
    app.config.from_object(configurations.get(env, "shhh.config.ProductionConfig"))

    register_extensions(app)

    with app.app_context():
        register_blueprints(app)
        db.create_all()
        try:
            scheduler.start()
        except SchedulerAlreadyRunningError:
            pass
        assets.manifest = False
        assets.cache = False
        try:
            compile_assets(assets)
        except RegisterError:
            pass

    app.context_processor(inject_global_vars)
    app.after_request(optimize_response)
    app.after_request(security_headers)

    app.register_error_handler(HTTPStatus.NOT_FOUND.value, not_found_error)
    app.register_error_handler(HTTPStatus.INTERNAL_SERVER_ERROR.value, internal_server_error)

    return app


def register_blueprints(app):
    """Register application blueprints."""
    app.register_blueprint(api)
    app.register_blueprint(views)


def register_extensions(app):
    """Register application extensions."""
    assets.init_app(app)
    db.init_app(app)
    try:
        scheduler.init_app(app)
    except SchedulerAlreadyRunningError:
        pass


def compile_assets(app_assets):
    """Configure and build asset bundles."""
    js_assets = ("create", "created", "read")
    css_assets = ("styles",)
    for code in js_assets:
        bundle = Bundle(f"src/js/{code}.js", filters="jsmin", output=f"dist/js/{code}.min.js")
        app_assets.register(code, bundle)
        bundle.build()
    for style in css_assets:
        bundle = Bundle(
            f"src/css/{style}.css", filters="cssmin", output=f"dist/css/{style}.min.css"
        )
        app_assets.register(style, bundle)
        bundle.build()


def inject_global_vars():
    """Global Jinja variables."""
    return {"version": __version__}


def not_found_error(error):
    """Not found error handler."""
    return rt("error.html", error=error), HTTPStatus.NOT_FOUND.value


def internal_server_error(error):
    """Internal server error handler."""
    return rt("error.html", error=error), HTTPStatus.INTERNAL_SERVER_ERROR.value


def optimize_response(response):
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


# pylint: disable=line-too-long
def security_headers(response):
    """Add required security headers."""
    response.headers.add("X-Frame-Options", "SAMEORIGIN")
    response.headers.add("X-Content-Type-Options", "nosniff")
    response.headers.add("X-XSS-Protection", "1; mode=block")
    response.headers.add("Referrer-Policy", "no-referrer-when-downgrade")
    response.headers.add(
        "Strict-Transport-Security", "max-age=63072000; includeSubdomains; preload"
    )
    response.headers.add(
        "Content-Security-Policy",
        "default-src 'self'; img-src 'self'; object-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
    )
    response.headers.add(
        "feature-policy",
        "accelerometer 'none'; camera 'none'; geolocation 'none'; gyroscope 'none'; magnetometer 'none'; microphone 'none'; payment 'none'; usb 'none'",
    )
    return response
