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

    def test_make_orders(self):
        '''tetst authenticated users can make orders'''
        self.meal1.save()
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        data = {'meal_id': self.meal1.meal_id, 'quantity': 1}
        
        response = self.client.post(ORDERS_URL, data=json.dumps(data), headers=headers)
        self.assertEqual(201, response.status_code)
        expected = 'Order has been placed'
        self.assertEqual(expected, json.loads(response.data)['message'])

    def test_edit_order(self):
        '''test authenticated users can edit orders'''
        self.meal1.save()

        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        # get menu
        data = {'meal_id': self.meal1.meal_id, 'quantity': 1}
        # place order
        response = self.client.post(ORDERS_URL, data=json.dumps(data), headers=headers)
        self.assertEqual(201, response.status_code)
        order = json.loads(response.data)['order']
        order_id = order.get('order_id')
        
        # put request to edit order
        data = {'new_data': {'meal_id':self.meal1.meal_id, 'quantity': 2}}
        url = ORDERS_URL + '/{}'.format(order_id)
        response = self.client.put(url, data=json.dumps(data),
                                   headers=headers)
        self.assertEqual(200, response.status_code)
        expected = 'Order modified succesfully'
        self.assertEqual(expected, json.loads(response.data)['message'])

    def test_get_all_orders(self):
        '''test admin can get all orders'''
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        response = self.client.get(ORDERS_URL, headers=headers)
        self.assertEqual(200, response.status_code)
        orders = self.order_model.get_all()
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
        self.meal1.save()
        data = {'meal_id': self.meal1.meal_id, 'quantity': 1}
        res = self.client.post(ORDERS_URL, headers=headers, data=json.dumps(data))
        self.assertEqual(201, res.status_code)
        response = self.client.get(ORDERS_URL, headers=headers)
        # self.assertEqual(200, response.status_code)
        user = self.user_model.get(username=self.test_user['username'])
        orders = self.order_model.query.filter_by(owner=user).all()
        orders = [order.make_dict() for order in orders]
        expected = {'message': 'All Orders',
                    'orders': orders}
        self.assertEqual(expected, json.loads(response.data))
