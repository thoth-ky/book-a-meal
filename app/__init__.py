'''Initialize app'''
from flask import Flask
from flask_restful import Api

# local imports
from config import config


def create_app(config_name):
    '''This function creates a flask app using the configuration setting passed
    the value for config can be either: 'development', 'testing'. 
    These act as deictionary keys and call up the specific
    configuration setting'''

    # create fllask app
    app = Flask(__name__)
    # insert configurations
    app.config.from_object(config[config_name])

    # import view resources and models here to avoid circular imports
    from . import models
    from . import views

    # create flask api
    api = Api(app)

    # add api resources

    return app