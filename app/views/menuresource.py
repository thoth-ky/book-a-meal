'''This is where code for api resources will go'''
from flask_restful import Resource, Api
from flask import request

# local imports
from ..models.menu import Menu
from ..models.user import User
from .. import DATABASE
from . import Blueprint


class MenuResource(Resource):
    '''Resource for managing Menu'''
    def post(self):
        '''handle post request to set up menu'''
        try:
            auth_header = request.headers.get('Authorization')
            access_token = auth_header.split(' ')[1]
            if access_token:
                username = User.decode_token(access_token)
                user = DATABASE.get_user_by_username(username)
                try:
                    if user.admin:
                        json_data = request.get_json(force=True)
                        meals_list = json_data.get('meal_list')
                        date = json_data.get('date', '')
                        if meals_list:
                            menu_object = Menu(meals=meals_list, date=date)
                            err = DATABASE.add(menu_object)
                            if err:
                                return{'Error': str(err)}, 202
                            return {'message': 'Menu created successfully'}, 201
                        return {'message': 'menu object can not be empty'}, 202
                    return {'message': 'Unauthorized'}, 401
                except Exception as error:
                    return {
                        'message': 'Unauthorized',
                        'Error': str(error)
                    }, 401
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400

    def get(self):
        '''handle GET requests'''
        try:
            auth_header = request.headers.get('Authorization')
            access_token = auth_header.split(' ')[1]
            if access_token:
                username = User.decode_token(access_token)
                user = DATABASE.get_user_by_username(username)
                try:
                    if user:
                        menu_items = DATABASE.current_menu
                        menu = [menu_items[item].make_dict() for item in menu_items]
                        return {
                            'message': 'Menu request succesful',
                            'menu': menu
                        }, 200
                except AttributeError as error:
                    return {
                        'message': 'Unauthorized',
                        'Error': str(error)
                    }, 401
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400

MENU_API = Blueprint('app.views.menuresource', __name__)
API = Api(MENU_API)
API.add_resource(MenuResource, '/menu', endpoint='menu')
