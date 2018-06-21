'''home bueprint'''
from flask_restful import Resource, Api
from flask import request
# local imports
from . import Blueprint
from ..helpers.decorators import token_required


class HomeResource(Resource):
    '''Display ,message at root url'''
    def get(self):
        '''handle GET method'''
        return 'Welcome to Hot Corner Delicacies', 200


class ProfileResource(Resource):
	'''Display User Profile'''
	@token_required
	def get(self, user):
		'''return user profile information'''
		user_info = user.view()
		return {'profile': user_info},  200



HOME_API = Blueprint('app.views.home', __name__)
API = Api(HOME_API)
API.add_resource(HomeResource, '/home', endpoint='home')
API.add_resource(ProfileResource, '/profile', endpoint='my_profile')
