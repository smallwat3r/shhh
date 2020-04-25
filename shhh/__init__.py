import logging
from os import path

from celery import Celery
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

ROOT_PATH = path.dirname(path.abspath(__file__))
db = SQLAlchemy()


def create_app(env):
    app = Flask(__name__)

    configurations = {
        "dev-local": "shhh.config.DefaultConfig",
        "dev-docker": "shhh.config.DockerConfig",
        "production": "shhh.config.ProductionConfig",
    }
    app.config.from_object(
        configurations.get(env, "shhh.config.ProductionConfig"))

    db.init_app(app)

    with app.app_context():
        celery = Celery(app.name,
                        broker=app.config["CELERY_BROKER_URL"],
                        backend=app.config["CELERY_RESULT_BACKEND"])

        logging.basicConfig(
            level=logging.INFO,
            format=("[%(asctime)s] [sev %(levelno)s] [%(levelname)s] "
                    "[%(name)s]> %(message)s"),
            datefmt="%a, %d %b %Y %H:%M:%S")

        logging.getLogger("werkzeug").setLevel(logging.WARNING)
        logger = logging.getLogger("shhh")

        from .api import api
        app.register_blueprint(api)

        from . import views

        db.create_all()
        return app
