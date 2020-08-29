import enum
import logging
import os

from flask import Flask

from flask_assets import Bundle
from shhh.api import api
from shhh.extensions import assets, db, scheduler


@enum.unique
class EnvConfig(enum.Enum):
    """Environment config values."""

    TESTING = "testing"
    DEV_LOCAL = "dev-local"
    DEV_DOCKER = "dev-docker"
    HEROKU = "heroku"
    PRODUCTION = "production"


def create_app(env=os.environ.get("FLASK_ENV")):
    """Application factory."""
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "[%(asctime)s] [sev %(levelno)s] [%(levelname)s] [%(name)s]> %(message)s"
        ),
        datefmt="%a, %d %b %Y %H:%M:%S",
    )

    if env == EnvConfig.TESTING.value:
        logging.getLogger("shhh").setLevel(logging.CRITICAL)
        logging.getLogger("apscheduler").setLevel(logging.CRITICAL)

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
        scheduler.start()

        assets.manifest = False
        assets.cache = False
        compile_assets(assets)

        from shhh import views  # pylint: disable=unused-import

    app.after_request(add_security_headers)
    return app


def register_blueprints(app):
    """Register application blueprints."""
    app.register_blueprint(api)


def register_extensions(app):
    """Register application extensions."""
    assets.init_app(app)
    db.init_app(app)
    scheduler.init_app(app)


def compile_assets(app_assets):
    """Configure and build asset bundles."""
    js_assets = ("create", "created", "read", "utils/errorParser", "utils/fetchRetry")
    css_assets = ("styles",)
    for code in js_assets:
        bundle = Bundle(
            f"src/js/{code}.js", filters="jsmin", output=f"dist/js/{code}.min.js"
        )
        app_assets.register(code, bundle)
        bundle.build()
    for style in css_assets:
        bundle = Bundle(
            f"src/css/{style}.css", filters="cssmin", output=f"dist/css/{style}.min.css"
        )
        app_assets.register(style, bundle)
        bundle.build()


def add_security_headers(response):
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
        "default-src 'self'; img-src 'self'; object-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",  # pylint: disable=line-too-long
    )
    response.headers.add(
        "feature-policy",
        "accelerometer 'none'; camera 'none'; geolocation 'none'; gyroscope 'none'; magnetometer 'none'; microphone 'none'; payment 'none'; usb 'none'",  # pylint: disable=line-too-long
    )
    return response
