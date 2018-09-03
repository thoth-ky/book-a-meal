'''Menu Blueprint'''
from datetime import datetime
from flask import request
from flask_restful import Resource, Api

# local imports
from . import Blueprint
from ..models.models import Menu, Meal
from ..helpers.decorators import token_required, admin_token_required
from ..helpers.email import send_updated_menu

def validate_meal_lists(meals_list):
    '''sanitize post data'''
    if not isinstance(meals_list, list):
        raise TypeError('Make meal_list a list of Meal object IDs')

def validate_date_input(date):
    '''validate that date input is valid'''
    try:
        day, month, year = date.split('-')
        return datetime(year=int(year), month=int(month), day=int(day))
    except (TypeError, ValueError):
        raise TypeError('Ensure date is provided using format DD-MM-YYYY')


class MenuResource(Resource):
    '''Resource for managing Menu'''
    @staticmethod
    @admin_token_required
    def post(user):
        '''handle post request to set up menu'''
        today = datetime.utcnow()
        json_data = request.get_json(force=True)
        meals_list = json_data.get('meal_list', '')
        date = json_data.get('date', f'{today.day}-{today.month}-{today.year}')

        try:
            validate_meal_lists(meals_list)
            date = validate_date_input(date)
        except TypeError as err:
            return {'error': str(err)}, 400

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
            msg = '{} successfully added to the menu for {}'.format(meal.name, strftime("%d-%m-%Y"))
            response = {
                'message': msg,
                'menu_id': menu.id,
                'menu': menu.view()
                }
            menu_meals = menu.view()['meals']
            # start thread to send mail independently
            send_updated_menu(menu_meals)
            return response, 201
        return {
            'message': 'Menu object can not be empty'
        }, 202

    @staticmethod
    @token_required
    def get(user):
        '''handle GET requests'''
        default_meals = Meal.get(default=True)
        today = datetime.utcnow().date()
        today = datetime(year=today.year, month=today.month, day=today.day)
        menu = Menu.get_by_date(date=today)
        
        if not menu:
            return {
                'message':'No menu found for {}'.format(today.ctime()),
                'menu':{
                    'meals':[],
                    'date': today.ctime()
                    }
            }, 404
        return {
            'message': 'Menu request succesful',
            'menu': menu,
            'user': user.admin
        }, 200


MENU_API = Blueprint('app.views.menuresource', __name__)
API = Api(MENU_API)
API.add_resource(MenuResource, '/menu', endpoint='menu')
