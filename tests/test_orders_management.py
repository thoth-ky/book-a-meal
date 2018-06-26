'''Tests for api endpoints'''
import json, time
from datetime import datetime, timedelta
# local imports
from . import BaseTestClass

SIGNUP_URL = '/api/v2/auth/signup'
SIGNIN_URL = '/api/v2/auth/signin'
MEALS_URL = '/api/v2/meals'
MENU_URL = 'api/v2/menu'
ORDERS_URL = 'api/v2/orders'
REMOVE_ORDERS_MEALS = 'api/v2/orders/1'
FAKE_ORDERS_MEALS = 'api/v2/orders/10'
ORDERS_MGMT_URL = 'api/v2/orders/serve/1'
ORDERS_MGMT_URL2 = 'api/v2/orders/serve/10'


class TestOrdersManagement(BaseTestClass):
    '''Tests for OrderResource '''
    def create_meals(self):
        '''helper to add meals and menu items'''
        admin = self.user_model(
            username='admin1', email='admin1', password='admin1234')
        admin.admin = True
        admin.save()
        self.meal1.user_id = admin.user_id
        self.meal2.user_id = admin.user_id
        self.meal1.save()
        self.meal2.save()
        self.menu.add_meal([self.meal1, self.meal2]) 
        self.menu.save()

    def test_make_orders(self):
        '''tetst authenticated users can make orders'''
        self.create_meals()
        access_token = self.login_user()
        headers = dict(Authorization='Bearer {}'.format(access_token))
        due_time = datetime.utcnow() + timedelta(minutes=40)
        due_time = f'{due_time.day}-{due_time.month}-{due_time.year} {due_time.hour}-{due_time.minute}'

        data = {'due_time': due_time, 'order':[{'meal_id':self.meal1.meal_id, 'quantity':2}]}
        response = self.client.post(
            ORDERS_URL, data=json.dumps(data), headers=headers)
        # self.assertEqual(201, response.status_code)
        expected = 'Order has been placed'
        self.assertEqual(expected, json.loads(response.data)['message'])

    def test_edit_order(self):
        '''test authenticated users can edit orders'''
        self.create_meals()
        # create order in the past
        self.user2.save()

        order = self.order_model(user_id=self.user2.user_id)
        order.add_meal_to_order(meal=self.meal1)
        order.save()

        access_token = self.user2.generate_token().decode()
        headers = dict(Authorization='Bearer {}'.format(access_token))

        url = '{}/1'.format(ORDERS_URL)
        new_data = {'new_data':{'meal_id': 1, 'quantity': 3}}

        response = self.client.put(
            url, data=json.dumps(new_data), headers=headers)
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
        data = {'username':self.user1.username, 'password':'password'}
        res = self.client.post(SIGNIN_URL, data=json.dumps(data))
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization=f'Bearer {access_token}')    
        # user1 makes order
        order = self.order_model(user_id=self.user1.user_id)
        order.add_meal_to_order(meal=self.meal1)
        order.save()
        # user2 makes order
        order = self.order_model(user_id=self.user2.user_id)
        order.add_meal_to_order(meal=self.meal2)
        order.save()
        # get user1 orders 
        response = self.client.get(ORDERS_URL, headers=headers)
        self.assertEqual(200, response.status_code)
        orders = self.order_model.query.filter_by(
            user_id=self.user1.user_id).all()
        orders = [order.view() for order in orders]
        expected = {'message': 'All Orders',
                    'orders': orders}
        self.assertEqual(expected, json.loads(response.data))

    def test_passing_bad_datatype_for_meal_id(self):
        '''test if order made using wrong datatype fails'''
        access_token = self.login_user()
        bad_data = {'due_time':'2-2-2018 1500', 'order':[{'meal_id': 1.2, 'quantity': 2}]}
        headers = dict(Authorization='Bearer {}'.format(access_token))
        res = self.client.post(
            ORDERS_URL, data=json.dumps(bad_data), headers=headers)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            'Inputs should be integers', json.loads(res.data)['error'])
    
    def test_ordering_with_invalid_meal_id(self):
        '''test error returned if order dne with non existent meal_id'''
        
        self.meal2.save()
        self.menu2.add_meal(self.meal2)
        self.menu2.save()
        self.user1.save()

        # no meals exist in db
        bad_data = {
            'order':[{'meal_id': 100, 'quantity': 2}],
            'due_time':'19-04-2019 09-00'}
        access_token = self.user1.generate_token().decode()
        headers = dict(Authorization='Bearer {}'.format(access_token))

        res = self.client.post(
            ORDERS_URL, data=json.dumps(bad_data), headers=headers)
        self.assertEqual(201, res.status_code)
        expected = [100]
        self.assertEqual(expected, json.loads(res.data)['meals_not_found'])
    
    def test_quantity_should_be_whole_number(self):
        '''test meal quantity only valid is it is a whole number'''
        expected = 'Inputs should be integers'
        bad_data = {'due_time':'2-2-2018 1500', 'order':[{'meal_id': 1, 'quantity': 2.5}]}
        access_token = self.login_user()
        headers = dict(Authorization='Bearer {}'.format(access_token))
        res = self.client.post(
            ORDERS_URL, data=json.dumps(bad_data), headers=headers)
        self.assertEqual(400, res.status_code)
        self.assertEqual(expected, json.loads(res.data)['error'])
    
    def test_get_unavailable_order(self):
        '''Test attempt to access an unavailable order'''
        access_token =self.login_admin()
        headers = dict(Authorization='Bearer {}'.format(access_token))
        res = self.client.get(ORDERS_URL+'/1', headers=headers)
        self.assertEqual(404, res.status_code)
        expected = {'message':'Order does not exist'}
        
        self.assertEqual(expected, json.loads(res.data))
        res = self.client.get(ORDERS_URL, headers=headers)
        self.assertEqual(404, res.status_code)
        expected = 'No order to display'
        self.assertEqual(expected, json.loads(res.data)['message'])
    
    def test_editing_unavailable_order(self):
        '''test attempt to edit an unavailable order'''
        access_token = self.login_user()
        headers = dict(Authorization='Bearer {}'.format(access_token))
        data = {'new_data': {'meal_id':1, 'quantity': 2}}
        url = ORDERS_URL + '/1'
        response = self.client.put(url, data=json.dumps(data),
                                   headers=headers)
        self.assertEqual(404, response.status_code)
        expected = 'You do not have such a order'
        self.assertEqual(expected, json.loads(response.data)['message'])

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
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        res = self.client.get(ORDERS_URL+'/1', headers=headers)
        self.assertEqual(res.status_code, 200)
        # log in user, not owner and try accessing order
        access_token = self.login_user()
        headers = dict(Authorization='Bearer {}'.format(access_token))
        res = self.client.get(ORDERS_URL+'/1', headers=headers)
        self.assertEqual(res._status_code, 401)

    def test_cant_edit_order_after_settime(self):
        '''test user cannot edit order after set time'''
        self.create_meals()
        # create order in the past
        self.user2.save()

        then = time.time() - 1200
        order = self.order_model(
            user_id=self.user2.user_id, time_ordered=then)
        order.add_meal_to_order(meal=self.meal1)
        order.save()
        creds = dict(username=self.user2.username, password='password')
        res = self.client.post(SIGNIN_URL, data=json.dumps(creds))
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        url = '{}/1'.format(ORDERS_URL)
        new_data = {'new_data':{'meal_id': 1, 'quantity': 3}}
        res = self.client.put(
            url, data =json.dumps(new_data), headers=headers)
        self.assertEqual(403, res.status_code)
        self.assertEqual(
            "Sorry you can not edit this order, either required time has elapsed or it has been served already",
            json.loads(res.data)['message'])
        
    def test_place_order_with_invalid_due_date(self):
        '''test what placing orders with invalid due dates
        gives an error message'''
        bad_data = {
            'order':[{'meal_id': 1, 'quantity': 2}],
            'due_time':'109-04-2019 0900'}
        self.user1.save()
        # no meals exist in db
        access_token = self.user1.generate_token().decode()
        headers = dict(Authorization='Bearer {}'.format(access_token))
        res = self.client.post(
            ORDERS_URL, data=json.dumps(bad_data), headers=headers)
        self.assertEqual(400, res.status_code)
        expected = 'Ensure date-time value is of the form "DD-MM-YY HH-MM"'
        self.assertEqual(expected, json.loads(res.data)['error'])

    def test_place_order_day_without_menu(self):
        '''test placing order before menu is created fails'''
        bad_data = {
            'order':[{'meal_id': 1, 'quantity': 2}],
            'due_time':'19-04-2019 09-00'}
        self.user1.save()
        # no meals exist in db
        access_token = self.user1.generate_token().decode()
        headers = dict(Authorization='Bearer {}'.format(access_token))
        due_time = datetime(year=2019, month=4, day=19)
        res = self.client.post(
            ORDERS_URL, data=json.dumps(bad_data), headers=headers)
        # self.assertEqual(202, res.status_code)
        expected = "Menu for {} not available".format(due_time.ctime())
        self.assertEqual(expected, json.loads(res.data)['message'])

    def test_place_order_with_due_less_than_30(self):
        '''test to ensure order with due time less than 30 mins from now fails'''
        self.create_meals()
        due_time = datetime.utcnow() + timedelta(minutes=5)
        due_time = '{}-{}-{} {}-{}'.format(
            due_time.day, due_time.month, due_time.year,
            due_time.hour, due_time.minute)
        order = {
            'order':[{"meal_id": 1, "quantity": 3}],
            'due_time': str(due_time)}
        self.user1.save()
        access_token = self.user1.generate_token().decode()
        headers = dict(Authorization='Bearer {}'.format(access_token))
        res = self.client.post(
            ORDERS_URL, data=json.dumps(order), headers=headers)
        self.assertEqual(202, res.status_code)
        expected = 'Unable to place order'
        self.assertEqual(expected, json.loads(res.data)['message'])
        self.assertEqual(expected, json.loads(res.data)['message'])

    def test_only_admin_can_mark_order_served(self):
        self.create_meals()

        # user1 orders meal1
        self.user1.save()
        order = self.order_model(user_id=self.user1.user_id)
        order.add_meal_to_order(meal=self.meal1)
        order.save()

        creds = dict(username='admin1', password='admin1234')
        res = self.client.post(SIGNIN_URL, data=json.dumps(creds))
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))

        user_token = self.user1.generate_token().decode()
        user_header = dict(Authorization=f'Bearer {user_token}')
        # for an existing order using admin token
        res = self.client.patch(ORDERS_MGMT_URL, headers=headers)
        self.assertEqual(200, res.status_code)
        self.assertEqual(json.loads(res.data)["message"], "Order processed and served")
        # for a non-existent order
        res = self.client.patch(ORDERS_MGMT_URL2, headers=headers)
        self.assertEqual(404, res.status_code)
        self.assertEqual(json.loads(res.data)["message"], "Order not found")

        # for an existing order using a user token
        res = self.client.patch(ORDERS_MGMT_URL, headers=user_header)
        self.assertEqual(401, res.status_code)
    
    def test_can_remove_meal_from_order(self):
        self.create_meals()
        self.user1.save()
        order = self.order_model(user_id=self.user1.user_id)
        order.add_meal_to_order(meal=self.meal1)
        order.save()

        creds = dict(username='admin1', password='admin1234')
        res = self.client.post(SIGNIN_URL, data=json.dumps(creds))
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))

        user_token = self.user1.generate_token().decode()
        user_header = dict(Authorization=f'Bearer {user_token}')
        meals_to_remove = {'meal_ids':[1]}
        res = self.client.patch(REMOVE_ORDERS_MEALS, data=json.dumps(meals_to_remove), headers=user_header)
        self.assertEqual(200, res.status_code)
        self.assertEqual([], json.loads(res.data)['order']['meals'])

        # remove meal from a non-existent meal
        res = self.client.patch(FAKE_ORDERS_MEALS, data=json.dumps(meals_to_remove), headers=user_header)
        self.assertEqual(404, res.status_code)
        self.assertEqual('You do not have such a order', json.loads(res.data)['message'])

    def test_cannot_edit_served_meals(self):
        self.create_meals()
        self.user1.save()
        order = self.order_model(user_id=self.user1.user_id)
        order.add_meal_to_order(self.meal1)
        order.is_served = True
        order.save()
        user_token = self.user1.generate_token().decode()
        user_header = dict(Authorization=f'Bearer {user_token}')
        meals_to_remove = {'meal_ids':[1]}
        res = self.client.patch(REMOVE_ORDERS_MEALS, data=json.dumps(meals_to_remove), headers=user_header)
        self.assertEqual(403, res.status_code)
        self.assertEqual("Sorry you can not edit this order, either required time has elapsed or it has been served already", json.loads(res.data)['message'])