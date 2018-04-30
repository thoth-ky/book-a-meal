'''Initialize app'''
from flask import Flask, Blueprint
from flask_restful import Api

# local imports
try:
    from config.config import config_dict
except ModuleNotFoundError:
    from ..config.config import config_dict

from .models.database import Database


DATABASE = Database()

from .views.home import HOME_API

def create_app(config_name):
    '''This function creates a flask app using the configuration setting passed
    the value for config can be either: 'development', 'testing'. 
    These act as deictionary keys and call up the specific
    con .gitifiguration setting'''

    # create fllask app
    app = Flask(__name__)
    
    
    # insert configurations
    app.config.from_object(config_dict[config_name])
    app.url_map.stict_slashes = False

    app.register_blueprint(HOME_API, url_prefix='/api/v1')
    return app
