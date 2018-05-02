'''Tests for api endpoints'''
import json

# local imports
from . import BaseTestClass

SIGNUP_URL = '/api/v1/auth/signup'
SIGNIN_URL = '/api/v1/auth/signin'
MEALS_URL = '/api/v1/meals'
MENU_URL = 'api/v1/menu'
ORDERS_URL = 'api/v1/orders'


class TestOrdersManagement(BaseTestClass):
    '''Tests for OrderResource '''
    def setup_menu(self):
        '''this is a helper function, to setup menu to ease testing of placing orders'''
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        
        meal1 = self.meal_model(
            meal_id=1, name='Fish', price=100, description='Tasty Tilapia')
        meal2 = self.meal_model(
            meal_id=2, name='Ugali', price=50, description='Tasty Ugali')
        self.database.add(meal1)
        self.database.add(meal2)

        # serialize 
        meal1 = meal1.make_dict()
        meal2 = meal2.make_dict()
        menu = {'meal_list': [meal1, meal2]}
        
        response = self.client.post(MENU_URL, data=json.dumps(menu), headers=headers)
        return response

    def test_make_orders(self):
        '''tetst authenticated users can make orders'''
        res = self.setup_menu()
        self.assertEqual(201, res.status_code)

        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        response = self.client.get(MENU_URL, headers=headers)
        self.assertEqual(200, response.status_code)
        current_menu = json.loads(response.data)['menu']
        meal_to_order = current_menu[0]
        data = {'order_id': 1, 'meal': meal_to_order, 'quantity': 1}
        
        response = self.client.post(ORDERS_URL, data=json.dumps(data), headers=headers)
        self.assertEqual(201, response.status_code)
        expected = 'Order has been placed'
        self.assertEqual(expected, json.loads(response.data)['message'])

    def test_edit_order(self):
        '''test authenticated users can edit orders'''
        res = self.setup_menu()
        self.assertEqual(201, res.status_code)

        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        # get menu
        response = self.client.get(MENU_URL, headers=headers)
        self.assertEqual(200, response.status_code)
        current_menu = json.loads(response.data)['menu']
        meal_to_order = current_menu[0]
        data = {'order_id': 2, 'meal': meal_to_order, 'quantity': 1}
        # place order
        response = self.client.post(ORDERS_URL, data=json.dumps(data), headers=headers)
        self.assertEqual(201, response.status_code)
        order = json.loads(response.data)['order']
        order_id = order.get('order_id')
        
        # put request to edit order
        data = {'new_data': {'quantity': 2}}
        url = ORDERS_URL + '/{}'.format(order_id)
        response = self.client.put(url, data=json.dumps(data),
                                   headers=headers)
        self.assertEqual(200, response.status_code)
        expected = {'message': 'Order modified succesfully'}
        self.assertEqual(expected, json.loads(response.data))

    def test_get_all_orders(self):
        '''test admin can get all orders'''
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        response = self.client.get(ORDERS_URL, headers=headers)
        self.assertEqual(200, response.status_code)
        orders = self.database.orders
        orders = [orders[item].make_dict() for item in orders]
        expected = {'message': 'All Orders',
                    'orders': orders}
        self.assertEqual(expected, json.loads(response.data))

    def test_user_only_get_own_orders(self):
        '''test only admin can access orders'''
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))

        response = self.client.get(ORDERS_URL, headers=headers)
        self.assertEqual(200, response.status_code)
        orders = self.database.user_orders
        orders = [orders[item].make_dict() for item in orders]
        expected = {'message': 'All Orders',
                    'orders': orders}
        self.assertEqual(expected, json.loads(response.data))
