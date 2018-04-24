'''This is where code for api resources will go'''

from flask_restful import Resource


class UserRegistrationResource(Resource):
    '''Manage user registration when method is POST'''
    pass


class LoginResource(Resource):
    '''Manage user log in'''
    pass


class MealResource(Resource):
    '''Resource for managing meals'''
    pass


class MenuResource(Resource):
    '''Resource for managing Menu'''
    pass


class OrderResource(Resource):
    '''Resource for managing Orders'''
    pass