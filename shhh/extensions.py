from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy

# All extensions are used as singletons and
# initialized in application factory.

db = SQLAlchemy()
scheduler = APScheduler()
