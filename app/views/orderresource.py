'''This is where code for api resources will go'''
from flask_restful import Resource, Api
from flask import request

# local imports
from . import Blueprint
from ..models.models import Order, User, Meal
from ..helpers.decorators import token_required, admin_token_required


class OrderResource(Resource):
    '''Resource for managing Orders'''
    @admin_token_required
    def post(self, user):
        '''place orders'''
        try:
            post_data = request.get_json(force=True)
            order_id = post_data.get('order_id')
            meal_id = post_data.get('meal')
            quantity = post_data.get('quantity')
            order = Order(owner=user, quantity=quantity, meal_id=meal_id)
            order.save()
            return {'message': 'Order has been placed', 'order': order.make_dict()}, 201
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400
    @token_required
    def get(self, order_id=None):
        '''get orders'''
        try:
            if order_id:
                order = DATABASE.orders.get(str(order_id), '')
                if order.order_by == username or user.admin:
                    return {'message': 'Order {} retrieved'.format(order_id)}, 200
            else:
                if not user.admin:
                    orders = Order.get(user_id=user_id)
                else:
                    orders = Order.get_all()
                orders = [order.make_dict() for order in orders]
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
            order = Order.get(owner=user)
            order.update(new_data)
            return {'message': 'Order modified succesfully'}, 200
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400

ORDER_API = Blueprint('app.views.orderresource', __name__)
API = Api(ORDER_API)
API.add_resource(OrderResource, '/orders', endpoint='orders')
API.add_resource(OrderResource, '/orders/<order_id>', endpoint='order')
