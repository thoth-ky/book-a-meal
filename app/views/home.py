'''home bueprint'''
from flask_restful import Resource, Api
from flask import request

# local imports
from . import Blueprint



class HomeResource(Resource):
    '''Display ,message at root url'''
    def get(self):
        '''handle GET method'''
        return 'Welcome to BAM API', 200


HOME_API = Blueprint('app.views.home', __name__)
API = Api(HOME_API)
API.add_resource(HomeResource, '/', endpoint='home')