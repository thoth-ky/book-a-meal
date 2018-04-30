'''home bueprint'''
from flask_restful import Resource, Api
from flask import request

# local imports
from . import Blueprint

HOME_BLUEPRINT = Blueprint('home', __name__)


class HomeResource(Resource):
    '''Display ,message at root url'''
    def get(self):
        '''handle GET method'''
        return 'Welcome to BAM API', 200


HOME_API = Blueprint('app.views.home', __name__)
api = Api(HOME_API)
api.add_resource(HomeResource, '/', endpoint='home')