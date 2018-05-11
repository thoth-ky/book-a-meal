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
        data = {'order':[[1,1]]}
        
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
        data = {'order':[[1,1]]}
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
        # create an order
        self.meal1.save()
        self.user1.save()
        order = self.order_model(user_id=self.user1.user_id)
        order.add_meal_to_order(meal=self.meal1)
        order.save()
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))

        response = self.client.get(ORDERS_URL, headers=headers)
        self.assertEqual(200, response.status_code)
        orders = self.order_model.get_all()
        orders = [order.view() for order in orders]
        expected = {'message': 'All Orders',
                    'orders': orders}
        self.assertEqual(expected, json.loads(response.data))

    def test_user_only_get_own_orders(self):
        '''test only admin can access orders'''
        self.user1.save()
        self.user2.save()
        creds = {'username':self.user1.username, 'password': 'password'}
        res = self.client.post(SIGNIN_URL, data=json.dumps(creds))
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        self.meal1.save()
        self.meal2.save()
        
        # user1 makes order
        order = self.order_model(user_id=self.user1.user_id)
        order.add_meal_to_order(meal=self.meal1)
        order.save()
        # user2 makes order
        order = self.order_model(user_id=self.user2.user_id)
        order.add_meal_to_order(meal=self.meal2)
        order.save()
        response = self.client.get(ORDERS_URL, headers=headers)
        self.assertEqual(200, response.status_code)
        orders = self.order_model.query.filter_by(user_id=self.user1.user_id).all()
        orders = [order.view() for order in orders]
        expected = {'message': 'All Orders',
                    'orders': orders}
        self.assertEqual(expected, json.loads(response.data))

    def test_passing_bad_datatype_for_meal_id(self):
        res = self.login_user()
        bad_data = {'order':[[1.2,1]]}
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        res = self.client.post(ORDERS_URL, data=json.dumps(bad_data), headers=headers)
        self.assertEqual(res.status_code, 400)
        self.assertEqual('Menu ids should be integers', json.loads(res.data)['Error'])
    
    def test_ordering_with_invalid_meal_id(self):
        res = self.login_user()
        # no meals exist in db
        bad_data = {'order':[[1,1]]}
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        res = self.client.post(ORDERS_URL, data=json.dumps(bad_data), headers=headers)
        self.assertEqual(400, res.status_code)
        expected = 'Invalid meal id 1 provided'
        self.assertEqual(expected, json.loads(res.data))
    
    def test_quantity_should_be_whole_number(self):
        expected = 'Quantity should be a whole number e.g 1, 2,4'
        bad_data = {'order':[[1, 1.2]]}
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        res = self.client.post(ORDERS_URL, data=json.dumps(bad_data), headers=headers)
        self.assertEqual(400, res.status_code)
        self.assertEqual(expected, json.loads(res.data)['Error'])
    
    def test_get_unavailable_order(self):
        res =self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        res = self.client.get(ORDERS_URL+'/1', headers=headers)
        self.assertEqual(404, res.status_code)
        expected = {'message':'Order does not exist'}
        self.assertEqual(expected, json.loads(res.data))
        res = self.client.get(ORDERS_URL, headers=headers)
        self.assertEqual(404, res.status_code)
        expected = 'No order to display'
        self.assertEqual(expected, json.loads(res.data))
    
    def test_editing_unavailable_order(self):
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        data = {'new_data': {'meal_id':1, 'quantity': 2}}
        url = ORDERS_URL + '/1'
        response = self.client.put(url, data=json.dumps(data),
                                   headers=headers)
        self.assertEqual(404, response.status_code)
        expected = 'You do not have such a order'
        self.assertEqual(expected, json.loads(response.data))

    def test_access_order_by_id(self):
        self.meal1.save()
        self.user1.save()
        order = self.order_model(user_id=self.user1.user_id)
        order.add_meal_to_order(meal=self.meal1)
        order.save()
        # login owner
        creds = {'username':self.user1.username, 'password':'password'}
        res = self.client.post(SIGNIN_URL, data =json.dumps(creds))
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        res = self.client.get(ORDERS_URL+'/1', headers=headers)
        self.assertEqual(res.status_code, 200)
        # log in user, not owner
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        res = self.client.get(ORDERS_URL+'/1', headers=headers)
        self.assertEqual(res._status_code, 401)
