from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

from instance.config import app_configuration

db =  SQLAlchemy()

def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_configuration[config_name])
    app.config.from_pyfile("config.py")
    db.init_app(app)
    return app
