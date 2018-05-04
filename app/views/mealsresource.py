'''home bueprint'''
from flask_restful import Resource, Api
from flask import request

# local imports
from . import Blueprint
from ..models.models import User, Meal
from ..helpers.decorators import token_required, admin_token_required


class MealResource(Resource):
    '''Resource for managing meals'''
    @admin_token_required
    def post(self, user):
        '''Add a meal'''
        try:
            post_data = request.get_json(force=True)
            name = post_data.get('name')
            price = post_data.get('price')
            description = post_data.get('description')
            meal = Meal(
                name=name, price=price,
                description=description)
            err = meal.save()
            if err:
                return {
                    'message': 'Meal not added',
                    'error': err}, 202
            return {'message': 'New meal created'}, 201
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400

    @admin_token_required
    def get(self, user, meal_id=None):
        '''Get all meals, if meal_id is specified, get a specific meal'''
        try:
            if meal_id:
                meal = Meal.get(meal_id=meal_id)
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
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400

    @admin_token_required
    def delete(self,user, meal_id):
        '''delete a specified meal'''
        try:
            meal = Meal.get(meal_id=meal_id)
            meal.delete()
            return {
                'message': 'Meal {} deleted'.format(meal_id),
            }, 200
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400

    @admin_token_required
    def put(self, user, meal_id):
        '''edit a specified meal id'''
        try:
            json_data = request.get_json(force=True)
            new_data = json_data['new_data']
            meal = Meal.get(meal_id=meal_id)
            err = meal.update(new_data)
            if err:
                return {'Error': err}
            return {
                'message': 'Meal {} edited'.format(meal_id),
            }, 202
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400


MEAL_API = Blueprint('app.views.mealsresource', __name__)
API = Api(MEAL_API)
API.add_resource(MealResource, '/meals', endpoint='meals')
API.add_resource(MealResource, '/meals/<meal_id>', endpoint='meal')
