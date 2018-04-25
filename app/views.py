'''This is where code for api resources will go'''
import json
from flask_restful import Resource
from .models import database, Menu, Meal, User, Admin, Order, Database
from flask import request

app_db = Database()


class UserRegistrationResource(Resource):
    '''Manage user registration when method is POST'''
    def post(self):
        '''handle the POST request to register users'''
        try:
            post_data = json.loads(request.data)
            username = post_data.get('username')
            password = post_data.get('password')
            email = post_data.get('email')
            admin = post_data.get('admin', '')
            if admin:
                # register user using Admin model
                admin = Admin(
                    username=username, password=password, email=email,
                    admin=admin)
                try:
                    app_db.add(item=admin)
                except ItemAlreadyExists as e:
                    return {
                        'message': 'User already exists',
                        'error': str(e)
                    }, 202
                return {
                    'message': 'Admin registration succesful, proceed to login'
                }, 201

            else:
                # register normal user
                user = User(username=username, password=password, email=email)
                try:
                    app_db.add(item=user)
                except Exception as e:
                    return {
                        'message': 'User already exists',
                        'error': str(e)
                    }, 202
                return {
                    'message': 'User registration succesful, proceed to login'
                    }, 201

        except Exception as e:
            return {
                'message': 'Encountered an error during registration',
                'Error': str(e)
            }, 400


class LoginResource(Resource):
    '''Manage user log in'''
    def post(self):
        try:
            post_data = json.loads(request.data)
            username = post_data.get('username', '')
            email = post_data.get('email', '')
            password = post_data.get('password')
            if username:
                user = app_db.get_user_by_username(username)
            elif email:
                user = app_db.get_user_by_email(email)
            else:
                user = None
            if user and User.validate_password(user, password):
                access_token = user.generate_token(username).decode()
                return {
                    'message': 'Successfully logged in',
                    'access_token': access_token
                }, 200
            else:
                return {
                    'message': 'The username/email or password provided is not correct'}, 401
        except Exception as e:
            return {
                'message': 'Encountered an error during log in',
                'Error': str(e)
            }, 400


class MealResource(Resource):
    '''Resource for managing meals'''
    def post(self):
        '''Add a meal'''
        try:
            auth_header = request.headers.get('Authorization')
            access_token = auth_header.split(' ')[1]
            if access_token:
                username = User.decode_token(access_token)
                user = app_db.get_user_by_username(username)
                try:
                    if user.admin:
                        post_data = json.loads(request.data)
                        meal_id = post_data.get('meal_id')
                        name = post_data.get('name')
                        price = post_data.get('price')
                        description = post_data.get('description')
                        meal = Meal(
                            meal_id=meal_id, name=name, price=price,
                            description=description)
                        err = app_db.add(meal)
                        if err:
                            return {
                                'message': 'Meal not added',
                                'error': err,
                                }, 202
                        return {'message': 'New meal created'}, 201
                except AttributeError as e:
                    return {'message': 'Not authorized for this action',
                            'Error': str(e)}, 401
        except Exception as e:
            return {
                'message': 'an error occured',
                'Error': str(e)
            }, 400

    def get(self, meal_id=None):
        '''Get all meals, if meal_id is specified, get a specific meal'''
        try:
            auth_header = request.headers.get('Authorization')
            access_token = auth_header.split(" ")[1]
            if access_token:
                username = User.decode_token(access_token)
                user = app_db.get_user_by_username(username)
                try:
                    if user.admin:
                        if meal_id:
                            meal = app_db.meals.get(meal_id, '')
                            return {
                                'message': 'Meal {}'.format(meal_id),
                                'meals': meal
                            }, 200
                        else:
                            meals = app_db.meals
                            meals = [meals[meal].make_dict() for meal in meals]
                            return {
                                'message': 'Succesful request',
                                'data': meals
                            }, 200
                except AttributeError as e:
                    return {'message': 'Not authorized for this action'}, 401
        except Exception as e:
            return {
                'message': 'an error occured',
                'Error': str(e)
            }, 400

    def delete(self, meal_id):
        '''delete a specified meal'''
        try:
            auth_header = request.headers.get('Authorization')
            access_token = auth_header.split(' ')[1]
            if access_token:
                username = User.decode_token(access_token)
                user = app_db.get_user_by_username(username)
                try:
                    if user.admin:
                        del app_db.meals[meal_id]
                        return {
                            'message': 'Meal {} deleted'.format(meal_id),
                        }, 200
                except AttributeError as e:
                    return {
                        'message': 'Not authorized for this action',
                        'Error': str(e)
                    }, 401
        except Exception as e:
            return {
                'message': 'an error occured',
                'Error': str(e)
            }, 400

    def put(self, meal_id):
        '''edit a specified meal id'''
        try:
            auth_header = request.headers.get('Authorization')
            access_token = auth_header.split(' ')[1]
            if access_token:
                username = User.decode_token(access_token)
                user = app_db.get_user_by_username(username)
                try:
                    if user.admin:
                        json_data = json.loads(request.data)
                        new_data = json_data['new_data']
                        meal = app_db.meals.get(meal_id, '')
                        meal.update(new_data)
                        return {
                            'message': 'Meal {} edited'.format(meal_id),
                        }, 202
                except AttributeError as e:
                    return {
                        'message': 'Unauthorized',
                        'Error': str(e)
                    }, 401
        except Exception as e:
            return {
                'message': 'an error occured',
                'Error': str(e)
            }, 400


class MenuResource(Resource):
    '''Resource for managing Menu'''
    pass


class OrderResource(Resource):
    '''Resource for managing Orders'''
    pass