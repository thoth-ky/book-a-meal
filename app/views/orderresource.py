'''This is where code for api resources will go'''
from flask_restful import Resource, Api
from flask import request

# local imports
from . import Blueprint
from ..models.models import Order, User, Meal
from ..helpers.decorators import token_required, admin_token_required


def validate_order_inputs(meal_list=None, quantity=None):
    if meal_list:
        if isinstance(meal_list, list):
            for i in meal_list:
                if not isinstance(i, int):
                    return 'Menu ids should be integers'
    if quantity:
        if isinstance(quantity, list):
            for i in quantity:
                if not isinstance(i, int):
                    return 'Quantity should be a whole number e.g 1, 2,4'

class OrderResource(Resource):
    '''Resource for managing Orders'''
    @token_required
    def post(self, user):
        '''place orders'''
        # data should contain a dictionary with a list of lists specifying meal_id and quantity for each
        # data = {'order':[[1,2], [4,1]}
        post_data = request.get_json(force=True)
        order_data = post_data['order']
        meal_list = [i[0] for i in order_data]
        quantity = [i[1] for i in order_data]
        
        err = validate_order_inputs(meal_list=meal_list, quantity=quantity)
        if err:
            return {'Error': str(err)}, 400
        # create order first
        order = Order(user_id=user.user_id)
        for meal_id, q in zip(meal_list, quantity):
            meal = Meal.get(meal_id=meal_id)
            if meal:
                order.add_meal_to_order(quantity=q, meal=meal)
            else:
                return 'Invalid meal id {} provided'.format(meal_id), 400
        order.save()
        return {'message': 'Order has been placed', 'order': order.view()}, 201

    @token_required
    def get(self, user, order_id=None):
        '''get orders'''
        if order_id:
            order = Order.get(order_id=order_id)
            if not order:
                return {'message':'Order does not exist'} , 404
            if order.owner.user_id == user.user_id or user.admin:
                return {'message': 'Order {} retrieved'.format(order_id), 'order': order.view()}, 200
            return {'message': 'Unauthorized'}, 401
        else:
            if user.admin == True:
                orders = Order.get_all()
            else:
                orders = Order.query.filter_by(owner=user).all()
            if not orders:
                return 'No order to display', 404
            orders = [order.view() for order in orders]
            return {'message': 'All Orders',
                'orders': orders}

    @token_required
    def put(self, user, order_id):
        '''edit orders'''
        post_data = request.get_json(force=True)
        new_data = post_data['new_data']
        order = Order.get(owner=user, order_id=order_id)
        if not order:
            return 'You do not have such a order', 404
        meal_id = new_data['meal_id']
        quantity = new_data['quantity']
        if order.editable:
            order.update_order(meal_id, quantity)
            return {'message': 'Order modified succesfully', 'order': order.view()}, 200
        return {'message': 'Sorry, you can not edit this order.'}, 403

ORDER_API = Blueprint('app.views.orderresource', __name__)
API = Api(ORDER_API)
API.add_resource(OrderResource, '/orders', endpoint='orders')
API.add_resource(OrderResource, '/orders/<order_id>', endpoint='order')
