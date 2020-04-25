import logging
from os import environ

from cryptography.fernet import Fernet
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from shhh.api import api
from shhh.extensions import db, scheduler


def register_blueprints(app):
    """Register application blueprints."""
    app.register_blueprint(api)


def create_app(env=environ.get("FLASK_ENV")):
    """Application factory."""
    logging.basicConfig(
        level=logging.INFO,
        format=("[%(asctime)s] [sev %(levelno)s] [%(levelname)s] "
                "[%(name)s]> %(message)s"),
        datefmt="%a, %d %b %Y %H:%M:%S")
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    app = Flask(__name__)

    app.logger.info(f"Loading env {env}")
    configurations = {
        "dev-local": "shhh.config.DefaultConfig",
        "dev-docker": "shhh.config.DockerConfig",
        "heroku": "shhh.config.HerokuConfig",
        "production": "shhh.config.ProductionConfig",
    }
    app.config.from_object(
        configurations.get(env, "shhh.config.ProductionConfig"))

    db.init_app(app)
    # scheduler.init_app(app)

    with app.app_context():
        register_blueprints(app)
        db.create_all()
        # scheduler.start()

        from shhh import views

    return app
