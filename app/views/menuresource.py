'''This is where code for api resources will go'''
from flask_restful import Resource, Api
from flask import request
from datetime import datetime
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
            meals_list = json_data.get('meal_list', '')
            date = json_data.get('date', '')
            if not date:
                date = datetime.utcnow().date()
            if meals_list:
                meals = [Meal.get(meal_id=id) for id in meals_list]
                menu = Menu(date=date)
                menu.add_meal(meals) 
                # menu = Menu(date=datetime.utcnow().date())
                # meal1 = Meal(name='Rice & Beef', price=100.00, description='Rice with beef. Yummy.')
                # meal2 = Meal(name='Ugali Fish', price=150.00, description='Ugali and fish, Nyanza tings!')
            
                # menu.add_meal(meal1)
                # menu.add_meal(meal2)
                # menu.save()
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
            menu_items = Menu.get(date=datetime.utcnow().date())
            menu_items = [item.make_dict() for item in menu_items.meals]
            return {
                'message': 'Menu request succesful',
                'menu': menu_items
            }, 200
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400

MENU_API = Blueprint('app.views.menuresource', __name__)
API = Api(MENU_API)
API.add_resource(MenuResource, '/menu', endpoint='menu')
