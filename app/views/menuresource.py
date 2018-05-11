'''This is where code for api resources will go'''
from flask_restful import Resource, Api
from flask import request
from datetime import datetime
# local imports
from . import Blueprint
from ..models.models import Menu, Meal
from ..helpers.decorators import token_required, admin_token_required

def validate_menu_inputs(meals_list=[], date=None):
    if meals_list:
        if not isinstance(meals_list, list):
            return 'Make meal_list a list of Meal object IDs'
    if date:
        day, month, year = date.split('-')
        try:
            date = datetime(year=int(year), month=int(month), day=int(day))
        except Exception as e:
            return 'Ensure date is provided using format DD-MM-YYYY'

class MenuResource(Resource):
    '''Resource for managing Menu'''
    @admin_token_required
    def post(self, user):
        '''handle post request to set up menu'''
        json_data = request.get_json(force=True)
        meals_list = json_data.get('meal_list', '')
        date = json_data.get('date', '')
        err = validate_menu_inputs(meals_list=meals_list, date=date)
        if err:
            return {'error': err}, 400
        if date == '':
            date = datetime.utcnow().date()
        else:
            day, month, year = date.split('-')
            date = datetime(year=int(year), month=int(month), day=int(day))
        
        if meals_list:
            meals = []
            for id in meals_list:
                meal = Meal.get(meal_id=id)  # add owner=user so that caterer can only add their meals to menu
                if isinstance(meal, Meal):
                    meals.append(meal)
                else:
                    return 'Invalid meal_id {}'.format(id), 202
            menu = Menu(date=date)
            menu.add_meal(meals) 
            return {'message': 'Menu created successfully', 'menu': menu.view()}, 201
        return {'message': 'Menu object can not be empty'}, 202

    @token_required
    def get(self, user):
        '''handle GET requests'''
        today = datetime.utcnow().date()
        today = datetime(year=today.year, month=today.month, day=today.day)
        menu = Menu.get(date=today)
        if not menu:
            return 'No menu found for {}'.format(today.ctime()), 404

        return {
            'message': 'Menu request succesful',
            'menu': menu.view()
        }, 200


MENU_API = Blueprint('app.views.menuresource', __name__)
API = Api(MENU_API)
API.add_resource(MenuResource, '/menu', endpoint='menu')
