'''Tests for api endpoints'''
import json, time

# local imports
from . import BaseTestClass

SIGNUP_URL = '/api/v1/auth/signup'
SIGNIN_URL = '/api/v1/auth/signin'
MEALS_URL = '/api/v1/meals'
MENU_URL = 'api/v1/menu'
ORDERS_URL = 'api/v1/orders'


class TestOrdersManagement(BaseTestClass):
    '''Tests for OrderResource '''
    def create_meals(self):
        admin = self.user_model(username='admin1', email='admin1', password='admin1234')
        admin.admin = True
        admin.save()
        self.meal1.user_id = admin.user_id
        self.meal2.user_id = admin.user_id
        self.meal1.save()
        self.meal2.save()



    def test_make_orders(self):
        '''tetst authenticated users can make orders'''
        self.create_meals()
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        data = {'order':[{'meal_id':self.meal1.meal_id, 'quantity':2}]}
        
        response = self.client.post(ORDERS_URL, data=json.dumps(data), headers=headers)
        self.assertEqual(201, response.status_code)
        expected = 'Order has been placed'
        self.assertEqual(expected, json.loads(response.data)['message'])

    def test_edit_order(self):
        '''test authenticated users can edit orders'''
        self.create_meals()

        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        # get menu
        data = {'order':[{'meal_id':self.meal1.meal_id, 'quantity':2}]}
        # place order
        response = self.client.post(ORDERS_URL, data=json.dumps(data), headers=headers)
        self.assertEqual(201, response.status_code)
        order = json.loads(response.data)['order']
        order_id = order.get('order_id')
        
        # put request to edit order
        data = {'new_data': {'meal_id':self.meal1.meal_id, 'quantity': 5}}
        url = ORDERS_URL + '/{}'.format(order_id)
        response = self.client.put(url, data=json.dumps(data),
                                   headers=headers)
        self.assertEqual(200, response.status_code)
        expected = 'Order modified succesfully'
        self.assertEqual(expected, json.loads(response.data)['message'])

    def test_get_all_orders(self):
        '''test admin can get all orders'''
        # create an order
        self.create_meals()
        
        # user1 orders meal1
        self.user1.save()
        order = self.order_model(user_id=self.user1.user_id)
        order.add_meal_to_order(meal=self.meal1)
        order.save()

        # user2 orders meal2
        self.user2.save()
        order = self.order_model(user_id=self.user2.user_id)
        order.add_meal_to_order(meal=self.meal2)
        order.save()

        # login admin
        creds = dict(username='admin1', password='admin1234')
        res = self.client.post(SIGNIN_URL, data=json.dumps(creds))
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))

        response = self.client.get(ORDERS_URL, headers=headers)
        self.assertEqual(200, response.status_code)
        admin1 = self.user_model.get(username='admin1')
        orders = {str(meal.name):meal.order_view() for meal in admin1.meals}
        expected = {
                'message': 'All Orders',
                'orders': orders
            }
        self.assertEqual(expected, json.loads(response.data))

    def test_user_only_get_own_orders(self):
        '''test only admin can access orders'''
        self.create_meals()

        self.user1.save()
        self.user2.save()
        creds = {'username':self.user1.username, 'password': 'password'}
        res = self.client.post(SIGNIN_URL, data=json.dumps(creds))
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        
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
        '''test if order made using wrong datatype fails'''
        res = self.login_user()
        bad_data = {'order':[{'meal_id': 1.2, 'quantity': 2}]}
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        res = self.client.post(ORDERS_URL, data=json.dumps(bad_data), headers=headers)
        self.assertEqual(res.status_code, 400)
        self.assertEqual('Menu ids should be integers', json.loads(res.data)['Error'])
    
    def test_ordering_with_invalid_meal_id(self):
        '''test error returned if order dne with non existent meal_id'''
        res = self.login_user()
        # no meals exist in db
        bad_data = {'order':[{'meal_id': 1, 'quantity': 2}]}
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        res = self.client.post(ORDERS_URL, data=json.dumps(bad_data), headers=headers)
        self.assertEqual(400, res.status_code)
        expected = 'Invalid meal id 1 provided'
        self.assertEqual(expected, json.loads(res.data))
    
    def test_quantity_should_be_whole_number(self):
        '''test meal quantity only valid is it is a whole number'''
        expected = 'Quantity should be a whole number e.g 1, 2,4'
        bad_data = {'order':[{'meal_id': 1, 'quantity': 2.5}]}
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        res = self.client.post(ORDERS_URL, data=json.dumps(bad_data), headers=headers)
        self.assertEqual(400, res.status_code)
        self.assertEqual(expected, json.loads(res.data)['Error'])
    
    def test_get_unavailable_order(self):
        '''Test attempt to access an unavailable order'''
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
        '''test attempt to edit an unavailable order'''
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
        '''test order can be accessed using id'''
        self.create_meals()
        self.user1.save()
        order = self.order_model(user_id=self.user1.user_id)
        order.add_meal_to_order(meal=self.meal1)
        order.save()

        # login owner and try accessing order
        creds = {'username':self.user1.username, 'password':'password'}
        res = self.client.post(SIGNIN_URL, data =json.dumps(creds))
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        res = self.client.get(ORDERS_URL+'/1', headers=headers)
        self.assertEqual(res.status_code, 200)

        # log in user, not owner and try accessing order
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        res = self.client.get(ORDERS_URL+'/1', headers=headers)
        self.assertEqual(res._status_code, 401)

    # def test_cant_edit_order_after_settime(self):
    #     # create order in the past
    #     self.user2.save()

    #     then = time.time() - 120
    #     order = self.order_model(user_id=self.user2.user_id, time_ordered=then)
    #     order.save()
    #     creds = dict(username=self.user2.username, password='password')
    #     res = self.client.post(SIGNIN_URL, data=json.dumps(creds))
    #     self.assertEqual(200, res.status_code)
    #     access_token = json.loads(res.data)['access_token']
    #     headers = dict(Authorization='Bearer {}'.format(access_token))
    #     url = '{}/1'.format(ORDERS_URL)
    #     new_data = {'new_data':{'meal_id': 1, 'quantity': 1}}
    #     res = self.client.put(url, data =json.dumps(new_data), headers=headers)
    #     self.assertEqual('Sorry, you can not edit this order.', json.loads(res.data))
    #     self.assertEqual(403, res.status_code)
