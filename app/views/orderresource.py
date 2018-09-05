'''Order Resource'''
import time
from datetime import datetime
from flask import request
from flask_restful import Resource, Api

# local imports
from . import Blueprint
from ..models.models import Order, Meal, Menu
from ..models.authmodels import User
from ..helpers.decorators import token_required, admin_token_required

def validate_order_inputs(inputs=[]):
    '''sanitize post data'''
    for i in inputs:
        try:
            int(i)
        except:
            raise TypeError('Inputs should be integers')

def place_order(menu, order, meal_list, quantity):
    '''Place order'''
    meals = [meal['meal_id'] for meal in menu['meals']]
    not_found = []
    for meal_id, quant in zip(meal_list, quantity):
        # confirm meal is in menu for due_time
        if meal_id in meals:
            meal = Meal.get(meal_id=meal_id)
            order.add_meal_to_order(quantity=quant, meal=meal)
        else:
            not_found.append(meal_id)
    order.save()
    return order, not_found

def get_due_time(due_time):
    '''validate due_time'''
    try:
        date, time_ = due_time.split(' ')
        day, month, year = date.split('-')
        hour, minute = time_.split('-')
        return datetime(day=int(day), month=int(month), year=int(year),
                        hour=int(hour), minute=int(minute))
    except Exception:
        raise TypeError('Ensure date-time value is of the form "DD-MM-YYYY HH-MM"')

def get_daily_summaries(orders):
    summary = {}
    dates = set()
    for order in orders:
        date_ordered = datetime.fromtimestamp(order.time_ordered).strftime("%Y-%m-%d")
        dates.add(date_ordered)
        summary.update({date_ordered: []})
    
    for order in orders:
        for date in dates:
            date_ordered = datetime.fromtimestamp(order.time_ordered).strftime("%Y-%m-%d")
            if date == date_ordered:
                order_view = order.view()

                summary[date].append({'total': order_view['total'], 'order_id': order_view['order_id']})
    return summary
            



class OrderResource(Resource):
    '''Resource for managing Orders'''
    @token_required
    def post(self, user):
        '''place orders post_data = {'due_time':'2-2-2018 1500', 'order':[{'meal_id':1, 'quantity':2}, {},{}]}'''
        post_data = request.get_json(force=True)
        try:
            order_data = post_data['order']
            due_time = post_data.get('due_time')
            meal_list = [dictionary['meal_id'] for dictionary in order_data]
            quantity = [dictionary['quantity'] for dictionary in order_data]
            
            validate_order_inputs(meal_list)
            validate_order_inputs(quantity)
            due_time = get_due_time(due_time)
        except (KeyError, TypeError) as err:
            return {'error': str(err)}, 400
        
        if (due_time - datetime.utcnow()).total_seconds() < 1800:
            return {'message': 'Unable to place order',
                    'help': 'Order should be due atleast 30 minutes from time of placing the order',
                    'grace': (due_time - datetime.utcnow()).total_seconds(),
                    'due_time': due_time.isoformat(),
                    'now': datetime.utcnow().isoformat()
                    }, 202
        
        menu_date = datetime(year=due_time.year, month=due_time.month,
                             day=due_time.day)
        order = Order(user_id=user.user_id, due_time=due_time)
        menu = Menu.get_by_date(date=menu_date)

        if menu:
            meal_list = [int(i) for i in meal_list]
            quantity = [int(i) for i in quantity]
            order, not_found = place_order(menu, order, meal_list, quantity)
            return {
                'message': 'Order has been placed',
                'meals_not_found': not_found,
                'order': order.view()}, 201

        return {
            "message": "Menu for {} not available".format(menu_date.ctime())
        }, 202

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
            admin_orders = None
            daily_summaries = None
            if user.admin is True:
                admin_view =  Order.query.all()
                admin_orders = [order.view() for order in admin_view]
                daily_summaries = get_daily_summaries(admin_view)

            orders = Order.query.filter_by(owner=user).all()
            orders = [order.view() for order in orders]
            
            
            return {
                'message': 'All Orders',
                'orders': orders,
                'admin_orders': admin_orders,
                'daily_summaries': daily_summaries
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
            'message': "Sorry you can not edit this order, either required time has elapsed or it has been served already",
            'delta': time.time()-order.time_ordered
        }, 403

    @token_required
    def patch(self, user, order_id):
        '''remove meal from order'''
        meal_ids = request.get_json(force=True)['meal_ids']
        order = Order.get(owner=user, order_id=order_id)
        if not order:
            return {'message': 'You do not have such a order'}, 404

        if order.editable() is True:
            for id_ in meal_ids:
                order.remove_meal(id_)
            order.save()
            return {
                'message': 'Order modified succesfully',
                'order': order.view()
            }, 200
        return {
            'message': "Sorry you can not edit this order, either required time has elapsed or it has been served already"
        }, 403


class OrderManagement(Resource):
    '''Admin only functions on orders'''
    @admin_token_required
    def patch(self, user, order_id):
        '''update orders to served'''
        order = Order.get(order_id=order_id)
        if order:
            order.is_served = True
            order.save()
            return {"message": "Order processed and served"}, 200
        return {"message": "Order not found"}, 404

ORDER_API = Blueprint('app.views.orderresource', __name__)
API = Api(ORDER_API)
API.add_resource(OrderResource, '/orders', endpoint='orders')
API.add_resource(OrderResource, '/orders/<order_id>', endpoint='order')
API.add_resource(OrderResource, 'orders/edit/<order_id>', endpoint='edit_order')
API.add_resource(OrderManagement, '/orders/serve/<order_id>', endpoint='completeorder')
