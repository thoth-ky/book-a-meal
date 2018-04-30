'''This is where code for api resources will go'''
from flask_restful import Resource
from flask import request

# local imports
from ..models.order import Order
from ..models.user import User
from .. import  DATABASE
from . import Blueprint

ORDER_BLUEPRINT = Blueprint('order', __name__)

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

# instantiate resource as view
ORDER_VIEW = OrderResource.as_view('order_view')
# add url
ORDER_BLUEPRINT.add_url_rule(
	   '/v1/auth/signin', view_func=ORDER_VIEW, methods=['POST', 'GET', 'PUT'])
