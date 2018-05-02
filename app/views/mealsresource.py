'''home bueprint'''
from flask_restful import Resource, Api
from flask import request

# local imports
from ..models.meal import Meal
from ..models.user import User
from .. import  DATABASE
from . import Blueprint
from ..helpers.decorators import token_required, admin_token_required


class MealResource(Resource):
    '''Resource for managing meals'''
    @admin_token_required
    def post(self):
        '''Add a meal'''
        try:
            post_data = request.get_json(force=True)
            meal_id = post_data.get('meal_id')
            name = post_data.get('name')
            price = post_data.get('price')
            description = post_data.get('description')
            meal = Meal(
                meal_id=meal_id, name=name, price=price,
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
    def get(self, meal_id=None):
        '''Get all meals, if meal_id is specified, get a specific meal'''
        try:
            auth_header = request.headers.get('Authorization')
            access_token = auth_header.split(" ")[1]
            if access_token:
                username = User.decode_token(access_token)
                user = DATABASE.get_user_by_username(username)
                try:
                    if user.admin:
                        if meal_id:
                            meal = DATABASE.meals.get(meal_id, '')
                            return {
                                'message': 'Meal {}'.format(meal_id),
                                'meals': meal.make_dict()
                            }, 200
                        meals = DATABASE.meals
                        meals = [meals[meal].make_dict() for meal in meals]
                        return {
                            'message': 'Succesful request',
                            'data': meals
                        }, 200
                    return {'message': 'Unauthorized'}, 401
                except AttributeError as error:
                    return {'message': 'Not authorized for this action'}, 401
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400

    def delete(self, meal_id):
        '''delete a specified meal'''
        try:
            auth_header = request.headers.get('Authorization')
            access_token = auth_header.split(' ')[1]
            if access_token:
                username = User.decode_token(access_token)
                user = DATABASE.get_user_by_username(username)
                try:
                    if user.admin:
                        del DATABASE.meals[meal_id]
                        return {
                            'message': 'Meal {} deleted'.format(meal_id),
                        }, 200
                    return {'message': 'Unauthorized'}, 401
                except AttributeError as error:
                    return {
                        'message': 'Not authorized for this action',
                        'Error': str(error)
                    }, 401
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400

    def put(self, meal_id):
        '''edit a specified meal id'''
        try:
            auth_header = request.headers.get('Authorization')
            access_token = auth_header.split(' ')[1]
            if access_token:
                username = User.decode_token(access_token)
                user = DATABASE.get_user_by_username(username)
                try:
                    if user.admin:
                        json_data = request.get_json(force=True)
                        new_data = json_data['new_data']
                        meal = DATABASE.meals.get(meal_id)
                        meal.update(new_data)
                        return {
                            'message': 'Meal {} edited'.format(meal_id),
                        }, 202
                    return {'message': 'Unauthorized'}, 401
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


MEAL_API = Blueprint('app.views.mealsresource', __name__)
API = Api(MEAL_API)
API.add_resource(MealResource, '/meals', endpoint='meals')
API.add_resource(MealResource, '/meals/<meal_id>', endpoint='meal')
