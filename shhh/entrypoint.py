import enum
import logging

from apscheduler.schedulers import SchedulerAlreadyRunningError
from flask import Flask
from flask_assets import Bundle
from webassets.env import RegisterError

from shhh.api import api
from shhh.extensions import assets, db, scheduler
from shhh.security import add_security_headers


@enum.unique
class EnvConfig(enum.Enum):
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
