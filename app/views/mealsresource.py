'''home bueprint'''
from flask_restful import Resource, Api
from flask import request

# local imports
from . import Blueprint
from ..models.models import User, Meal
from ..helpers.decorators import token_required, admin_token_required

def validate_meal_data(name=None, price=None, description=None):
    if not isinstance(name, str) or len(name) <= 0:
        return 'Invalid meal name provided'
    try:
        price = float(price)
    except:
        return 'Invalid value for price'
    if not isinstance(description, str) or len(description) <= 0:
        return 'Invalid description'

class MealResource(Resource):
    '''Resource for managing meals'''
    @admin_token_required
    def post(self, user):
        '''Add a meal'''
        post_data = request.get_json(force=True)
        name = post_data.get('name', None)
        price = post_data.get('price', None)
        description = post_data.get('description', None)
        err = validate_meal_data(name=name, price=price, description=description)
        if err:
            return {'error': err}, 400
        meal = Meal(
            name=name, price=float(price),
            description=description)
        meal.save()
        return {'message': 'New meal created', 'meal': meal.make_dict()}, 201

    @admin_token_required
    def get(self, user, meal_id=None):
        '''Get all meals, if meal_id is specified, get a specific meal'''
        if meal_id:
            meal = Meal.get(meal_id=meal_id)
            if not isinstance(meal, Meal):
                return 'Meal {} not found'.format(meal_id), 404
            return {
                'message': 'Meal {}'.format(meal_id),
                'meals': meal.make_dict()
            }, 200
        meals = Meal.get_all()
        meals = [meal.make_dict() for meal in meals]
        return {
            'message': 'Succesful request',
            'data': meals
        }, 200

    @admin_token_required
    def delete(self,user, meal_id):
        '''delete a specified meal'''
        meal = Meal.get(meal_id=meal_id)
        if not meal:
            return 'Meal {} not found'.format(meal_id), 404
        meal.delete()
        return {
            'message': 'Meal {} deleted'.format(meal_id),
        }, 200

    @admin_token_required
    def put(self, user, meal_id):
        '''edit a specified meal id'''
        json_data = request.get_json(force=True)
        new_data = json_data['new_data']
        meal = Meal.get(meal_id=meal_id)
        meal.update(new_data)
        return {
            'message': 'Meal {} edited'.format(meal_id),
            'new': meal.make_dict()
        }, 202


MEAL_API = Blueprint('app.views.mealsresource', __name__)
API = Api(MEAL_API)
API.add_resource(MealResource, '/meals', endpoint='meals')
API.add_resource(MealResource, '/meals/<meal_id>', endpoint='meal')
