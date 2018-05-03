'''This is where code for api resources will go'''
from flask_restful import Resource, Api
from flask import request

# local imports
from . import Blueprint
from ..models.models import Menu, Meal
from ..helpers.decorators import token_required, admin_token_required


class MenuResource(Resource):
    '''Resource for managing Menu'''
    @admin_token_required
    def post(self, user):
        '''handle post request to set up menu'''
        try:
            json_data = request.get_json(force=True)
            meals_list = json_data.get('meal_list')
            date = json_data.get('date', '')
            if meals_list:
                menu = Menu(meals=meals_list, date=date)
                menu.save()
                return {'message': 'Menu created successfully'}, 201
            return {'message': 'menu object can not be empty'}, 202
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400

    @token_required
    def get(self, user):
        '''handle GET requests'''
        try:
            if user:
                menu_items = DATABASE.current_menu
                menu = [menu_items[item].make_dict() for item in menu_items]
                return {
                    'message': 'Menu request succesful',
                    'menu': menu
                }, 200
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400

MENU_API = Blueprint('app.views.menuresource', __name__)
API = Api(MENU_API)
API.add_resource(MenuResource, '/menu', endpoint='menu')
