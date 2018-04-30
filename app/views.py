'''This is where code for api resources will go'''
from flask_restful import Resource
from flask import request
# local imports
from .models import Menu, Meal, User, Admin, Order, ItemAlreadyExists
from . import  DATABASE


class HomeResource(Resource):
    '''Display ,message at root url'''
    def get(self):
        '''handle GET method'''
        return 'Welcome to BAM API', 200


class UserRegistrationResource(Resource):
    '''Manage user registration when method is POST'''
    def post(self):
        '''handle the POST request to register users'''
        try:
            post_data = request.get_json(force=True)
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
                    DATABASE.add(item=admin)
                except ItemAlreadyExists as error:
                    return {
                        'message': 'User already exists',
                        'error': str(error)
                    }, 202
                return {
                    'message': 'Admin registration succesful, proceed to login'
                }, 201

            # register normal user
            user = User(username=username, password=password, email=email)
            try:
                DATABASE.add(item=user)
            except Exception as error:
                return {
                    'message': 'User already exists',
                    'error': str(error)
                }, 202
            return {
                'message': 'User registration succesful, proceed to login'
                }, 201

        except Exception as error:
            return {
                'message': 'Encountered an error during registration',
                'Error': str(error)
            }, 400


class LoginResource(Resource):
    '''Manage user log in'''
    def post(self):
        '''Handles POST requests'''
        try:
            post_data = request.get_json(force=True)
            username = post_data.get('username', '')
            email = post_data.get('email', '')
            password = post_data.get('password')
            if username:
                user = DATABASE.get_user_by_username(username)
            elif email:
                user = DATABASE.get_user_by_email(email)
            else:
                user = None
            if user and User.validate_password(user, password):
                access_token = user.generate_token().decode()
                return {
                    'message': 'Successfully logged in',
                    'access_token': access_token
                }, 200
            return {
                'message': 'The username/email or password provided is not correct'}, 401
        except Exception as error:
            return {
                'message': 'Encountered an error during log in',
                'Error': str(error)
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
                user = DATABASE.get_user_by_username(username)
                try:
                    if user.admin:
                        post_data = request.get_json(force=True)
                        meal_id = post_data.get('meal_id')
                        name = post_data.get('name')
                        price = post_data.get('price')
                        description = post_data.get('description')
                        meal = Meal(
                            meal_id=meal_id, name=name, price=price,
                            description=description)
                        err = DATABASE.add(meal)
                        if err:
                            return {
                                'message': 'Meal not added',
                                'error': err,
                                }, 202
                        return {'message': 'New meal created'}, 201
                    else:
                        return {'message': 'Unauthorized'}, 401
                except AttributeError as error:
                    return {'message': 'Not authorized for this action',
                            'Error': str(error)}, 401
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400

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


class MenuResource(Resource):
    '''Resource for managing Menu'''
    def post(self):
        '''handle post request to set up menu'''
        try:
            auth_header = request.headers.get('Authorization')
            access_token = auth_header.split(' ')[1]
            if access_token:
                username = User.decode_token(access_token)
                user = DATABASE.get_user_by_username(username)
                try:
                    if user.admin:
                        json_data = request.get_json(force=True)
                        meals_list = json_data.get('meal_list')
                        date = json_data.get('date', '')
                        if meals_list:
                            menu_object = Menu(meals=meals_list, date=date)
                            err = DATABASE.add(menu_object)
                            if err:
                                return{'Error': str(err)}, 202
                            return {'message': 'Menu created successfully'}, 201
                        return {'message': 'menu object can not be empty'}, 202
                    return {'message': 'Unauthorized'}, 401
                except Exception as error:
                    return {
                        'message': 'Unauthorized',
                        'Error': str(error)
                    }, 401
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400

    def get(self):
        '''handle GET requests'''
        try:
            auth_header = request.headers.get('Authorization')
            access_token = auth_header.split(' ')[1]
            if access_token:
                username = User.decode_token(access_token)
                user = DATABASE.get_user_by_username(username)
                try:
                    if user:
                        menu_items = DATABASE.current_menu
                        menu = [menu_items[item].make_dict() for item in menu_items]
                        return {
                            'message': 'Menu request succesful',
                            'menu': menu
                        }, 200
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


class OrderResource(Resource):
    '''Resource for managing Orders'''
    def post(self):
        '''place orders'''
        try:
            auth_header = request.headers.get('Authorization')
            access_token = auth_header.split(' ')[1]
            if access_token:
                username = User.decode_token(access_token)
                user = DATABASE.get_user_by_username(username)
                try:
                    if user:
                        post_data = request.get_json(force=True)
                        order_id = post_data.get('order_id')
                        meal_id = post_data.get('meal')
                        quantity = post_data.get('quantity')

                        order = Order(order_id=order_id, username=username, quantity=quantity,
                                      meal=[meal_id])
                        err = DATABASE.add(order)
                        if err:
                            return {'Error': str(err)}
                        return {'message': 'Order has been placed', 'order': order.make_dict()}, 201

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

    def get(self, order_id=None):
        '''get orders'''
        try:
            auth_header = request.headers.get('Authorization')
            access_token = auth_header.split(' ')[1]
            if access_token:
                username = User.decode_token(access_token)
                user = DATABASE.get_user_by_username(username)
                try:
                    if user:
                        if order_id:
                            order = DATABASE.orders.get(str(order_id), '')
                            if order.order_by == username or user.admin:
                                return {'message': 'Order {} retrieved'.format(order_id)}, 200
                        else:
                            if not user.admin:
                                orders = DATABASE.user_orders.get(username, '')
                            else:
                                orders = DATABASE.orders
                            orders = [orders[item].make_dict() for item in orders]
                            return {'message': 'All Orders',
                                    'orders': orders}
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

    def put(self, order_id):
        '''edit orders'''
        try:
            auth_header = request.headers.get('Authorization')
            access_token = auth_header.split(' ')[1]
            if access_token:
                username = User.decode_token(access_token)
                user = DATABASE.get_user_by_username(username)
                try:
                    if user:
                        post_data = request.get_json(force=True)
                        new_data = post_data['new_data']
                        order = DATABASE.orders.get(order_id, '')
                        if order.order_by == username:
                            order.update(new_data)
                            return {'message': 'Order modified succesfully'}, 200
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
