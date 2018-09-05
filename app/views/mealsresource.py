'''Meal blueprint'''
from flask import request
from flask_restful import Resource, Api
# local imports
from . import Blueprint
from ..models.authmodels import Meal
from ..helpers.decorators import admin_token_required

def validate_meal_data(name=None, price=None, description=None):
    '''sanitize inputs'''
    msg = None
    if name != None and (not isinstance(name, str) or name.strip() == ""):
        msg = 'Invalid meal name provided'

    try:
        if price:
            price = float(price)
    except ValueError:
        msg = 'Invalid value for price'

    if description != None and (not isinstance(description, str)\
        or description.strip() == ""):
        msg = 'Invalid description'
    return msg


class MealResource(Resource):
    '''Resource for managing meals'''
    @staticmethod
    @admin_token_required
    def post(user):
        '''Add a meal'''
        post_data = request.get_json(force=True)
        name = post_data.get('name', '').lower()
        price = post_data.get('price', '')
        description = post_data.get('description', '')
        default = post_data.get('menu_default', False)
        err = validate_meal_data(name=name, price=price, description=description)
        meal = Meal.get(caterer=user, name=name)
        if meal is not None:
            err = "You already have a similar meal"
        if err:
            return {'message': err}, 203
        meal = Meal(
            name=name, price=float(price), user_id=user.user_id,
            description=description, default=default)
        meal.save()
        return {
            'message': 'New meal created',
            'meal': meal.view()
        }, 201

    @staticmethod
    @admin_token_required
    def get(user, meal_id=None):
        '''Get all meals, if meal_id is specified, get a specific meal'''
        if meal_id:
            meal = Meal.get(meal_id=meal_id, caterer=user)
            if not isinstance(meal, Meal):
                return {'message': 'Meal {} not found'.format(meal_id)}, 404
            return {
                'message': 'Meal {}'.format(meal_id),
                'meal': meal.view()
            }, 200
        meals = [meal.view() for meal in user.meals]
        return {
            'message': 'Succesful request',
            'meals': meals
        }, 200

    @staticmethod
    @admin_token_required
    def delete(user, meal_id):
        '''delete a specified meal'''
        meal = Meal.get(meal_id=meal_id, caterer=user)
        if not meal:
            return 'Meal {} not found'.format(meal_id), 404
        meal.delete()
        return {
            'message': 'Meal {} deleted'.format(meal_id),
        }, 200

    @staticmethod
    @admin_token_required
    def put(user, meal_id):
        '''edit a specified meal id'''
        new_data = request.get_json(force=True)['new_data']
        name = new_data.get('name', None)
        if name:
            name = name.lower()
        price = new_data.get('price', None)
        description = new_data.get('description', None)
        err = validate_meal_data(name=name, price=price, description=description)
        if err:
            return {'message': err}, 400
        meal = Meal.get(meal_id=meal_id, caterer=user)
        if not meal:
            return {'message': 'Meal not found'}, 404
        new_data = {'price': price, 'name': name, 'description': description}
        meal.update(new_data)
        return {
            'message': 'Meal {} edited'.format(meal_id),
            'new': meal.view()
        }, 202


MEAL_API = Blueprint('app.views.mealsresource', __name__)
API = Api(MEAL_API)
API.add_resource(
    MealResource,
    '/api/v2/meals',
    '/meals',
    endpoint='meals')
API.add_resource(
    MealResource,
    '/api/v2/meals/<meal_id>',
    '/meals/<meal_id>',
    endpoint='meal')
