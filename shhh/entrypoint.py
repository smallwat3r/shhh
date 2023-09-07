import gzip
import logging
from http import HTTPStatus
from io import BytesIO

from flask import Flask, Response, render_template as rt
from flask_apscheduler import APScheduler
from flask_assets import Bundle
from htmlmin.main import minify

from shhh import __version__, config
from shhh.adapters import orm
from shhh.api.api import api
from shhh.constants import EnvConfig
from shhh.extensions import assets, db, scheduler
from shhh.scheduler import tasks
from shhh.web import web


def create_app(env: EnvConfig) -> Flask:
    """Application factory."""
    logging.basicConfig(
        level=logging.INFO,
        format=("[%(asctime)s] [sev %(levelno)s] [%(levelname)s] "
                "[%(name)s]> %(message)s"),
        datefmt="%a, %d %b %Y %H:%M:%S",
    )
    app = Flask(__name__)
    config_obj = _get_config(env)
    app.config.from_object(config_obj)
    _register_extensions(app)

    with app.app_context():
        _register_blueprints(app)
        orm.start_mappers()

        scheduler._scheduler.start()
        _add_scheduler_jobs(scheduler)

        assets.manifest = False
        assets.cache = False
        _compile_static_assets(assets)

    app.context_processor(_inject_global_vars)
    _register_after_request_handlers(app)
    _register_error_handlers(app)
    return app


def _get_config(env: EnvConfig) -> type[config.DefaultConfig]:
    if env not in set(EnvConfig):
        raise RuntimeError(f"{env=} specified in FLASK_ENV is not supported")

    configurations = {
        EnvConfig.TESTING: config.TestConfig,
        EnvConfig.DEV_DOCKER: config.DevelopmentConfig,
        EnvConfig.HEROKU: config.HerokuConfig,
        EnvConfig.PRODUCTION: config.ProductionConfig,
    }
    return configurations[env]


def _register_after_request_handlers(app: Flask) -> None:
    app.after_request(_optimize_response)
    app.after_request(_add_required_security_headers)


def _register_error_handlers(app: Flask) -> None:
    app.register_error_handler(HTTPStatus.NOT_FOUND, _not_found_error)
    app.register_error_handler(HTTPStatus.INTERNAL_SERVER_ERROR,
                               _internal_server_error)


def _register_blueprints(app: Flask) -> None:
    app.register_blueprint(api)
    app.register_blueprint(web)


def _register_extensions(app: Flask) -> None:
    assets.init_app(app)
    db.init_app(app)
    scheduler.init_app(app)


def _add_scheduler_jobs(scheduler: APScheduler) -> None:
    scheduler.add_job(id="delete_expired_records",
                      func=tasks.delete_expired_records,
                      trigger="interval",
                      seconds=60)


def _compile_static_assets(app_assets) -> None:
    assets_to_compile = (("js", ("create", "created", "read")),
                         (("css", ("styles", ))))
    for k, v in assets_to_compile:
        for file in v:
            bundle = Bundle(f"src/{k}/{file}.{k}",
                            filters=f"{k}min",
                            output=f"dist/{k}/{file}.min.{k}")
            app_assets.register(file, bundle)
            bundle.build()


def _inject_global_vars() -> dict[str, str]:
    return {"version": __version__}


def _not_found_error(error) -> tuple[str, HTTPStatus]:
    return rt("error.html", error=error), HTTPStatus.NOT_FOUND


def _internal_server_error(error) -> tuple[str, HTTPStatus]:
    return rt("error.html", error=error), HTTPStatus.INTERNAL_SERVER_ERROR


def _optimize_response(response: Response) -> Response:
    """Minify HTML and use gzip compression."""
    if response.mimetype == "text/html":
        response.set_data(minify(response.get_data(as_text=True)))

    # do not gzip below 500 bytes or on JSON content
    if (response.content_length < 500
            or response.mimetype == "application/json"):
        return response

    response.direct_passthrough = False

    gzip_buffer = BytesIO()
    gzip_file = gzip.GzipFile(mode="wb", compresslevel=6, fileobj=gzip_buffer)
    gzip_file.write(response.get_data())
    gzip_file.close()

    response.set_data(gzip_buffer.getvalue())
    response.headers.add("Content-Encoding", "gzip")
    return response


def _add_required_security_headers(response: Response) -> Response:
    response.headers.add("X-Frame-Options", "SAMEORIGIN")
    response.headers.add("X-Content-Type-Options", "nosniff")
    response.headers.add("X-XSS-Protection", "1; mode=block")
    response.headers.add("Referrer-Policy", "no-referrer-when-downgrade")
    response.headers.add("Strict-Transport-Security",
                         "max-age=63072000; includeSubdomains; preload")
    response.headers.add(
        "Content-Security-Policy",
        ("default-src 'self'; img-src 'self'; object-src 'self'; "
         "script-src 'self' 'unsafe-inline'; "
         "style-src 'self' 'unsafe-inline'"))
    response.headers.add(
        "feature-policy",
        ("accelerometer 'none'; camera 'none'; geolocation 'none'; "
         "gyroscope 'none'; magnetometer 'none'; microphone 'none'; "
         "payment 'none'; usb 'none'"))
    return response
