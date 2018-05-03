'''home bueprint'''
from flask_restful import Resource, Api
from flask import request

# local imports
from ..models.models import User
from ..helpers.decorators import admin_token_required
from . import Blueprint

# Blueprint instance representing authentication blueprint


class UserRegistrationResource(Resource):
    '''Manage user registration when method is POST'''
    def post(self):
        '''handle the POST request to register users'''
        try:
            post_data = request.get_json(force=True)
            username = post_data.get('username')
            password = post_data.get('password')
            email = post_data.get('email')
            admin = post_data.get('admin', False)
            if User.has(username=username) or User.has(email=email):
                return{
                    'message': 'Username or Email not available.'
                }, 202
            user = User(username=username, password=password, email=email)
            user.save()
            if admin:
                User.promote_user(user)
                return {
                    'message': 'Admin registration succesful, proceed to login'
                }, 201

            # register normal user
            return {
                'message': 'User registration succesful, proceed to login'
                }, 201

        except Exception as error:
            return {
                'message': 'Encountered an error during registration',
                'Error': str(error)
            }, 400

    @admin_token_required
    def get(self, user):
        users = User.get_all()
        users = [user.make_dict() for user in users]
        return {'users':users}, 200

class LoginResource(Resource):
    '''Manage user log in'''
    def post(self):
        '''Handles POST requests'''
        try:
            post_data = request.get_json(force=True)
            username = post_data.get('username', '')
            email = post_data.get('email', '')
            password = post_data.get('password')
            if User.has(username=username) or User.has(email=email):
                # proceed to login user
                if email:
                    user = User.get(email=email)
                if username:
                    user = User.get(username=username)
                if user.validate_password(password):
                    access_token = user.generate_token().decode()
                    return {
                        'message': 'Successfully logged in',
                        'access_token': access_token
                    }, 200
            return {
                'message': 'The username/email or password provided is not correct'}, 401
        except Exception as error:
            return {
                'message': 'Encountered an error during log in',
                'Error': str(error)
            }, 400

AUTH_API = Blueprint('app.views.authresource', __name__)
API = Api(AUTH_API)
API.add_resource(UserRegistrationResource, '/auth/signup', endpoint='signup')
API.add_resource(LoginResource, '/auth/signin', endpoint='signin')
