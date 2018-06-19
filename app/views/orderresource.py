'''This is where code for api resources will go'''
from datetime import datetime, timedelta
from flask_restful import Resource, Api
from flask import request
import time
# local imports
from . import Blueprint
from ..models.models import Order, User, Meal, Menu
from ..helpers.decorators import token_required, admin_token_required


def validate_order_inputs(meal_list=None, quantity=None):
    '''sanitize post data'''
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
    def get_due_time(self, due_time):
        try:
            date, time = due_time.split(' ')
            day, month, year  = date.split('-')
            hour, minute = time.split('-')
            return datetime(day=int(day), month=int(month), year=int(year),
                            hour=int(hour), minute=int(minute))
        except Exception as e:
            return 'Ensure date-time value is of the form "DD-MM-YY HH-MM"'

    @token_required
    def post(self, user):
        '''place orders
        order_data = {'due':'2-2-2018 1500',order':[{'meal_id':1, 'quantity':2}, {},{}]}
        data should contain a dictionary with a list of dictionaries specifying meal_id and
        quantity for each as keys'''
        post_data = request.get_json(force=True)
        order_data = post_data['order']
        meal_list = [dictionary['meal_id'] for dictionary in order_data]
        quantity = [dictionary['quantity'] for dictionary in order_data]
        due_time = post_data.get('due_time', None)

        err = validate_order_inputs(meal_list=meal_list, quantity=quantity)

        if err:
            return {'Error': str(err)}, 400
        # create order first
        now = datetime.utcnow()
        if due_time:
            due_time = self.get_due_time(due_time)
            if isinstance(due_time, str):
                return {
                    'message':due_time,
                    'error':post_data.get('due_time')
                }, 400
        else:
            due_time = now + timedelta(minutes=30)

        if (due_time -now).total_seconds() < 1800:
            return {
                'message': 'Unable to place order',
                'help': 'Order should be due atleast 30 minutes from time\
                         of placing the order'
            }, 202
        menu_date = datetime(
            year=due_time.year, month=due_time.month, day=due_time.day)
        order = Order(user_id=user.user_id, due_time=due_time)
        menu = Menu.get(date=menu_date)
        if isinstance(menu, Menu):
            meals = [meal.meal_id for meal in menu.meals]
        else:
            return {
                "message":"Menu for {} not available".format(menu_date.ctime())
            }, 202

        for meal_id, quant in zip(meal_list, quantity):
            # confirm meal is in menu for due_time
            if meal_id in meals:
                meal = Meal.get(meal_id=meal_id)
                order.add_meal_to_order(quantity=quant, meal=meal)
            else:
                return 'Invalid meal id {} provided. Meal not in Menu'.format(
                    meal_id), 400
        order.save()
        return {
            'message': 'Order has been placed',
            'order': order.view()
        }, 201

    @token_required
    def get(self, user, order_id=None):
        '''get orders'''
        if order_id:
            order = Order.get(order_id=order_id)

            if not order:
                return {'message': 'Order does not exist'}, 404

            if order.owner.user_id == user.user_id or user.admin:
                return {
                    'message': 'Order {} retrieved'.format(order_id),
                    'order': order.view()}, 200
            return {'message': 'Unauthorized'}, 401
        else:
            if user.admin is True:
                orders =  {str(meal.name):meal.order_view() for meal in user.meals}
            else:
                orders = Order.query.filter_by(owner=user).all()
                orders = [order.view() for order in orders]
            if not orders:
                return {'message':'No order to display'}, 404
            return {
                'message': 'All Orders',
                'orders': orders
            }, 200

    @token_required
    def put(self, user, order_id):
        '''edit orders'''
        post_data = request.get_json(force=True)
        new_data = post_data['new_data']
        order = Order.get(owner=user, order_id=order_id)
        if not order:
            return {'message': 'You do not have such a order'}, 404
        meal_id = new_data['meal_id']
        quantity = new_data['quantity']

        if order.editable() is True:
            order.update_order(meal_id, quantity)
            return {
                'message': 'Order modified succesfully',
                'order': order.view()
            }, 200
        return {
            'message': 'Sorry, you can not edit this order.',
            'delta': time.time()-order.time_ordered
        }, 403


class OrderManagement(Resource):
    '''Admin only functions on orders'''    
    @admin_token_required
    def patch(self, user, order_id):
        '''update orders to served'''
        order = Order.get(order_id=order_id)
        if order:
            order.time_served = time.time()
            order.save()
            return {"message": "Order processed and served"}, 200
        return {"message": "Order not found"}, 404

ORDER_API = Blueprint('app.views.orderresource', __name__)
API = Api(ORDER_API)
API.add_resource(OrderResource, '/orders', endpoint='orders')
API.add_resource(OrderResource, '/orders/<order_id>', endpoint='order')
API.add_resource(OrderManagement, '/orders/serve/<order_id>', endpoint='completeorder')
