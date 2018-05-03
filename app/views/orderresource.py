'''This is where code for api resources will go'''
from flask_restful import Resource, Api
from flask import request

# local imports
from . import Blueprint
from ..models.models import Order, User, Meal
from ..helpers.decorators import token_required, admin_token_required


class OrderResource(Resource):
    '''Resource for managing Orders'''
    @token_required
    def post(self, user):
        '''place orders'''
        try:
            post_data = request.get_json(force=True)
            meal_id = post_data['meal_id']
            quantity = post_data.get('quantity')
            meal = Meal.get(meal_id=meal_id)
            order = Order(user_id=user.user_id)
            order.add_meal_to_order(quantity=quantity, meal=meal)
            order.save()
            return {'message': 'Order has been placed', 'order': order.make_dict()}, 201
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
                    order = dict(order_id=order.order_id,
                                 owner=order.owner,
                                 meals=[[a.meal.meal_id, a.meal.name, a.meal.price, a.quantity] for a in order.meal.all()])
                    return {'message': 'Order {} retrieved'.format(order_id), 'order': order.make_dict()}, 200
            else:
                print('----------')
                if not user.admin:
                    orders = Order.get(user_id=user.user_id)
                    
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
            order = Order.get(owner=user, order_id=order_id)
            order.update(new_data)
            return {'message': 'Order modified succesfully', 'order': order.make_dict()}, 200
        except Exception as error:
            return {
                'message': 'an error occured',
                'Error': str(error)
            }, 400

ORDER_API = Blueprint('app.views.orderresource', __name__)
API = Api(ORDER_API)
API.add_resource(OrderResource, '/orders', endpoint='orders')
API.add_resource(OrderResource, '/orders/<order_id>', endpoint='order')
