from flask_api import FlaskAPI
from .auth.views import auth_blueprint
from .models import db
from flask_cors import CORS

from instance.config import app_configuration



def create_app(config_name):
    """Creates flask api app."""
    app = FlaskAPI(__name__, instance_relative_config=True)
    CORS(app)
    app.config.from_object(app_configuration[config_name])
    app.config.from_pyfile("config.py")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.register_blueprint(auth_blueprint)
    db.init_app(app)
    return app
