'''Initialize app'''
from flask import Flask
from flask_restful import Api

# local imports
try:
    from config.config import config_dict
except ModuleNotFoundError:
    from ..config.config import config_dict

from .models import Database

app_db = Database()


def create_app(config_name):
    '''This function creates a flask app using the configuration setting passed
    the value for config can be either: 'development', 'testing'. 
    These act as deictionary keys and call up the specific
    con .gitifiguration setting'''

    # create fllask app
    app = Flask(__name__)
    
    # insert configurations
    app.config.from_object(config_dict[config_name])
    # import view resources and models here to avoid circular imports
    from .views import UserRegistrationResource, LoginResource, MealResource, MenuResource, OrderResource, HomeResource
    
    # create flask api
    api = Api(app)

    # add api resources
    api.add_resource(HomeResource, '/')
    api.add_resource(UserRegistrationResource, '/v1/auth/signup', '/v1/auth/signup/')
    api.add_resource(LoginResource, '/v1/auth/signin', '/v1/auth/signin')
    api.add_resource(MealResource, '/v1/meals', '/v1/meals/', '/v1/meals/<meal_id>/')
    api.add_resource(MenuResource, '/v1/menu', '/v1/menu/')
    api.add_resource(OrderResource, '/v1/orders', '/v1/orders/', '/v1/orders/<order_id>', '/v1/orders/<order_id>/')

    return app
