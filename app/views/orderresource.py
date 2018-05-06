'''This is where code for api resources will go'''
from flask_restful import Resource, Api
from flask import request

# local imports
from . import Blueprint
from ..models.models import Order, User, Meal
from ..helpers.decorators import token_required, admin_token_required


def validate_order_inputs(meal_list=None, quantity=None):
    if meal_list:
        if not isinstance(meal_list, list):
            return 'Put IDs of meals ordered in a python list []', 204
    if quantity:
        if not isinstance(quantity, int):
            return 'Quantity shuld be a whole number e.g 1, 2,4'


class OrderResource(Resource):
    '''Resource for managing Orders'''
    @token_required
    def post(self, user):
        '''place orders'''
        try:
            # data should contain a dictionary with a list of lists specifying meal_id and quantity for each
            # data = {'order':[[1,2], [4,1]}
            post_data = request.get_json(force=True)
            order_data = post_data['order']
            meal_list = [i[0] for i in order_data]
            quantity = [i[1] for i in order_data]
            
            validate_order_inputs(meal_list=meal_list, quantity=quantity)
            # create order first
            order = Order(user_id=user.user_id)
            for meal_id, q in zip(meal_list, quantity):
                meal = Meal.get(meal_id=meal_id)
                if meal:
                    order.add_meal_to_order(quantity=q, meal=meal)
                else:
                    return 'Invalid id {} provided'.format(meal_id)
            order.save()
            return {'message': 'Order has been placed', 'order': order.view()}, 201
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400
    @token_required
    def get(self, user, order_id=None):
        '''get orders'''
        try:
            if order_id:
                order = Order.get(order_id=order_id)
                if not order:
                    return {'Order does not exist'} , 404
                if order.owner == user or user.admin:
                    return {'message': 'Order {} retrieved'.format(order_id), 'order': order.view()}, 200
            else:
                if user.admin == True:
                    orders = Order.get_all()
                else:
                    orders = Order.query.filter_by(owner=user).all()
                if not orders:
                    return 'No order to display', 204
                orders = [order.view() for order in orders]
                return {'message': 'All Orders',
                    'orders': orders}
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400

    @token_required
    def put(self, user, order_id):
        '''edit orders'''
        try:
            post_data = request.get_json(force=True)
            new_data = post_data['new_data']
            order = Order.get(owner=user, order_id=order_id)
            if not order:
                return 'You do not have such a order', 204
            order.update(new_data)
            return {'message': 'Order modified succesfully', 'order': order.view()}, 200
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400

ORDER_API = Blueprint('app.views.orderresource', __name__)
API = Api(ORDER_API)
API.add_resource(OrderResource, '/orders', endpoint='orders')
API.add_resource(OrderResource, '/orders/<order_id>', endpoint='order')
