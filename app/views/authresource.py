'''Home Blueprint'''
from flask import request
from flask_restful import Resource, Api
# local imports
from ..models.authmodels import User, RevokedTokens
from ..helpers.decorators import super_admin_required, token_required
from . import Blueprint

def validate_user_details(username=None, email=None, password=None):
    '''sanitizing input'''
    msg = None
    if username:
        if not isinstance(username, str) or len(username) <= 3 or username.strip() == "":
            msg = 'Invalid username. Ensure username has more than 3 characters'
    if password:
        if not isinstance(password, str) or len(password) < 8 or password.strip() == "":
            msg = 'Invalid password. Ensure password is a string of not less than 8 characters'
    if email:
        if not isinstance(email, str) or not '@' in email or email.strip() == "" or not\
            email.endswith('.com'):
            msg = 'Invalid Email. Ensure email is valid and is of form "example@mail.com"'
    return msg


class UserRegistrationResource(Resource):
    '''Manage user registration when method is POST'''
    @staticmethod
    def post():
        '''handle the POST request to register users'''
        post_data = request.get_json(force=True)
        username = post_data.get('username')
        password = post_data.get('password')
        email = post_data.get('email')
        if username:
            username = username.lower()
        err = validate_user_details(
            username=username,
            email=email,
            password=password)
        if username is None or password is None or email is None:
            return {'message': 'Incomplete details'}, 400
        if err:
            return {'message':err}, 400
        if User.has(username=username) or User.has(email=email):
            return{
                'message': 'Username or Email not available.'
            }, 202
        user = User(username=username, password=password, email=email)
        user.save()
        access_token = user.generate_token().decode()
        return {
            'message': 'User registration succesful, and logged in. Your access token is',
            'access_token': access_token,
            'is_admin': user.admin
            }, 201


class UserManagementResource(Resource):
    '''user management by super admin'''
    @staticmethod
    @super_admin_required
    def get(user_id=None):
        '''Get a list of all users'''
        if user_id:
            user = User.get(user_id=user_id)
            if user:
                users = [user]
            else:
                return {'message': 'User not found'}, 404

        else:
            users = User.query.filter_by(is_active=True).all()

        users = [user.view() for user in users]
        return {'message':'User Info', 'users': users}, 200

    @staticmethod
    @super_admin_required
    def put(user_id):
        '''Promote user'''
        user_to_promote = User.get(user_id=user_id)
        User.promote_user(user_to_promote)
        return {'message': 'User has now been made admin', 'user':user_to_promote.view()}

    @staticmethod
    @super_admin_required
    def delete(user_id):
        '''delete user'''
        user = User.get(user_id=user_id, is_active=True)
        if user:
            user.is_active = False
            return {'message': 'User {} has been deactivated'.format(user_id)}, 200
        return {'message': 'User {} does not exist'.format(user_id)}, 404


class LoginResource(Resource):
    '''Manage user log in'''
    @staticmethod
    def post():
        '''Handles POST requests'''
        try:
            post_data = request.get_json(force=True)
            username = post_data.get('username', '').lower()
            email = post_data.get('email', '').lower()
            password = post_data.get('password')
            if email:
                err = validate_user_details(email=email)
            if username:
                err = validate_user_details(username=username)
            if err:
                return {'message': err}, 400
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
                        'access_token': access_token,
                        'is_admin': user.admin
                    }, 200
            return {
                'message': 'The username/email or password provided is not correct'
                }, 401
        except Exception as error:
            raise error


class LogoutResource(Resource):
    '''manage user logouts'''
    @staticmethod
    @token_required
    def get(user):
        '''handle GET requests'''
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(' ')[1]
        token_to_revoke = RevokedTokens(token=access_token)
        token_to_revoke.save()
        return {'message': f'{user.username} has been logged out successfully.'}, 200



AUTH_API = Blueprint('app.views.authresource', __name__)
API = Api(AUTH_API)
API.add_resource(
    UserRegistrationResource,
    '/auth/signup',
    '/signup',
    '/register',
    '/auth/register',
    endpoint='signup')
API.add_resource(
    LoginResource,
    '/auth/signin',
    '/auth/login',
    '/login',
    '/signin',
    endpoint='signin')
API.add_resource(
    UserManagementResource,
    '/users',
    endpoint='accounts')
API.add_resource(
    UserManagementResource,
    '/users/<user_id>',
    '/user/<user_id>',
    endpoint='account')
API.add_resource(
    UserManagementResource,
    '/users/promote/<user_id>',
    '/user/promote/<user_id>',
    endpoint='promote')
API.add_resource(
    LogoutResource,
    '/signout',
    '/auth/signout',
    '/logout',
    '/auth/logout',
    endpoint='signout')
