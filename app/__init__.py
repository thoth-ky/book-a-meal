'''Initialize app'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_mail import Mail
# local imports
try:
    from config.config import config_dict
except ModuleNotFoundError:
    from ..config.config import config_dict

DB = SQLAlchemy()
URL_PREFIX = '/api/v1'
AUTH = HTTPBasicAuth()
MAIL = Mail()

def create_app(config_name):
    '''This function creates a flask app using the configuration setting passed.
    The value for config can be either: 'development', 'testing'. These act as
    dictionary keys and call up the specific configuration setting'''

    # create flask app
    app = Flask(__name__)

    # insert configurations
    app.config.from_object(config_dict[config_name])
    app.url_map.strict_slashes = False
    DB.init_app(app)
    MAIL.init_app(app)

    # import blueprints here to avoid  circular imports
    from .views.home import HOME_API
    from .views.authresource import AUTH_API
    from .views.mealsresource import MEAL_API
    from .views.menuresource import MENU_API
    from .views.orderresource import ORDER_API

    # register blueprints
    app.register_blueprint(HOME_API, url_prefix=URL_PREFIX)
    app.register_blueprint(AUTH_API, url_prefix=URL_PREFIX)
    app.register_blueprint(MEAL_API, url_prefix=URL_PREFIX)
    app.register_blueprint(MENU_API, url_prefix=URL_PREFIX)
    app.register_blueprint(ORDER_API, url_prefix=URL_PREFIX)

    return app
