'''home bueprint'''
from flask_restful import Resource, Api
from flask import request

# local imports
from ..models.models import User
from ..helpers.decorators import admin_token_required, super_admin_required
from . import Blueprint

def validate_user_details(username=None, email=None, password=None, admin=None):
    # sanitizing input
    if username:
        if not isinstance(username, str) or len(username) <= 3:
            return 'Invalid username. Ensure username has more than 3 characters'
    if password:
        if not isinstance(password, str) or len(password)< 8:
            return'Invalid password. Ensure password is a string of not less than 8 characters'
    if email:
        if not isinstance(email, str) or not '@' in email:
            return 'Invalid Email'


class UserRegistrationResource(Resource):
    '''Manage user registration when method is POST'''
    def post(self):
        '''handle the POST request to register users'''
        post_data = request.get_json(force=True)
        username = post_data.get('username')
        password = post_data.get('password')
        email = post_data.get('email')
        admin = post_data.get('admin', False)
        err = validate_user_details(username=username, email=email, password=password, admin=admin)
        if username is None or password is None or email is None:
            return 'Incomplete details', 400
        if err:
            return {'ERR':err}, 400
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


class UserManagementResource(Resource):
    @super_admin_required
    def get(self, user_id=None):
        '''Get a list of all users'''
        if user_id:
            users =[User.get(user_id=user_id)]
            users = [user.make_dict() for user in users]
            return {'users':users}, 200
        users = User.get_all()
        users = [user.make_dict() for user in users]
        return {'users':users}, 200

    @super_admin_required
    def put(self, user_id):
        '''Promote user'''
        user_to_promote = User.get(user_id=user_id)
        User.promote_user(user_to_promote)
        return {'message': 'User has now been made admin', 'user':user_to_promote.make_dict()}
    @super_admin_required
    def delete(self, user_id):
        user = User.get(user_id=user_id)
        user.delete()
        return {'message': 'User {} has been deleted'.format(user_id)}, 200

class LoginResource(Resource):
    '''Manage user log in'''
    def post(self):
        '''Handles POST requests'''
        post_data = request.get_json(force=True)
        username = post_data.get('username', '')
        email = post_data.get('email', '')
        password = post_data.get('password')
        if email:
            err = validate_user_details(email=email)
        if username:
            err = validate_user_details(username=username)
        if err:
            return {'err': err}, 400
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
            return {'message': 'The username/email or password provided is not correct'}, 401
        return {
            'message': 'The username/email or password provided is not correct'}, 401


AUTH_API = Blueprint('app.views.authresource', __name__)
API = Api(AUTH_API)
API.add_resource(UserRegistrationResource, '/auth/signup', endpoint='signup')
API.add_resource(LoginResource, '/auth/signin', endpoint='signin')
API.add_resource(UserManagementResource, '/users', endpoint='accounts')
API.add_resource(UserManagementResource, '/users/<user_id>', endpoint='account')
API.add_resource(UserManagementResource, '/users/promote/<user_id>', endpoint='promote')
