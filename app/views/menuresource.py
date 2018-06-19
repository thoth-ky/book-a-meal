'''This is where code for api resources will go'''
from flask_restful import Resource, Api
from flask import request, current_app
from datetime import datetime
# local imports
from . import Blueprint
from ..models.models import Menu, Meal
from ..helpers.decorators import token_required, admin_token_required
from ..helpers.email import send_updated_menu
from threading import Thread


def validate_menu_inputs(meals_list=[], date=None):
    '''sanitize post data'''
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

        meals_list = [id_ for id_ in meals_list
                      if id_ in [meal.meal_id for meal in user.meals]]
        menu = Menu.get(date=date)

        if not menu:
            menu = Menu(date=date)

        if meals_list:
            meals = []
            for id_ in meals_list:
                meal = Meal.get(meal_id=id_, caterer=user)
                meals.append(meal)
            menu.add_meal(meals, date=date)
            menu.save()
            response = {
                'message': 'Menu created successfully',
                'menu_id': menu.id,
                'menu': menu.view()
                }
            menu_meals = menu.view()['meals']
            # start thread to send mail independently
            send_updated_menu(menu_meals)  # pragma: no cover
            
        
            return response, 201
        return {
            'message': 'Menu object can not be empty'
        }, 202

    @token_required
    def get(self, user):
        '''handle GET requests'''
        today = datetime.utcnow().date()
        today = datetime(year=today.year, month=today.month, day=today.day)
        menu = Menu.get(date=today)
        if not menu:
            return {'message':'No menu found for {}'.format(today.ctime())}, 404
        return {
            'message': 'Menu request succesful',
            'menu': menu.view()
        }, 200


MENU_API = Blueprint('app.views.menuresource', __name__)
API = Api(MENU_API)
API.add_resource(MenuResource, '/menu', endpoint='menu')
