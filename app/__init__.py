from flask_api import FlaskAPI
from .auth.views import auth_blueprint
from .events.views import event_blueprint
from .event_rsvp.views import rsvp_blueprint
from .error import not_found, not_allowed
from .error import internal_server_error, bad_request
from .models import db
from flask_cors import CORS

from instance.config import app_configuration


def create_app(config_name):
    """Creates flask api app."""
    app = FlaskAPI(__name__, instance_relative_config=True)
    CORS(app)
    app.url_map.strict_slashes = False
    app.config.from_object(app_configuration[config_name])
    app.config.from_pyfile("config.py")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(event_blueprint)
    app.register_blueprint(rsvp_blueprint)
    app.register_error_handler(Exception, internal_server_error)
    app.register_error_handler(400, bad_request)
    app.register_error_handler(404, not_found)
    app.register_error_handler(405, not_allowed)
    db.init_app(app)
    return app
