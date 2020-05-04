import logging
import os

from flask import Flask
from flask_assets import Bundle

from shhh.api import api
from shhh.extensions import assets, db, scheduler


def create_app(env=os.environ.get("FLASK_ENV")):
    """Application factory."""
    logging.basicConfig(
        level=logging.INFO,
        format=("[%(asctime)s] [sev %(levelno)s] [%(levelname)s] "
                "[%(name)s]> %(message)s"),
        datefmt="%a, %d %b %Y %H:%M:%S")

    # Disable werkzeug logging under WARNING.
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    if env == "testing":
        logging.getLogger("shhh").setLevel(logging.CRITICAL)
        logging.getLogger("apscheduler").setLevel(logging.CRITICAL)

    app = Flask(__name__)

    configurations = {
        "dev-local": "shhh.config.DefaultConfig",
        "testing": "shhh.config.TestConfig",
        "dev-docker": "shhh.config.DockerConfig",
        "heroku": "shhh.config.HerokuConfig",
        "production": "shhh.config.ProductionConfig",
    }
    app.config.from_object(
        configurations.get(env, "shhh.config.ProductionConfig"))

    register_extensions(app)

    with app.app_context():
        register_blueprints(app)

        db.create_all()
        scheduler.start()

        assets.manifest = False
        assets.cache = False
        compile_assets(assets)

        from shhh import views  # pylint: disable=unused-import

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
    js_assets = ("create", "created", "read", )
    css_assets = ("styles", )
    for code in js_assets:
        bundle = Bundle(f"src/js/{code}.js",
                        filters="jsmin",
                        output=f"dist/js/{code}.min.js")
        app_assets.register(code, bundle)
        bundle.build()
    for style in css_assets:
        bundle = Bundle(f"src/css/{style}.css",
                        filters="cssmin",
                        output=f"dist/css/{style}.min.css")
        app_assets.register(style, bundle)
        bundle.build()
