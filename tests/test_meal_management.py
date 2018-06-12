'''Tests for api endpoints'''
import json

# local imports
from . import BaseTestClass

SIGNUP_URL = '/api/v2/auth/signup'
SIGNIN_URL = '/api/v2/auth/signin'
MEALS_URL = '/api/v2/meals'
MENU_URL = 'api/v2/menu'
ORDERS_URL = 'api/v2/orders'


class TestMealsManagement(BaseTestClass):
    '''Test for MEal Resource'''
    def test_get_all_meals(self):
        '''test client can get all meals'''
        # login admin user
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization="Bearer {}".format(access_token))
        # populate meals
        self.create_meal()
        response = self.client.get(MEALS_URL, headers=headers)
        self.assertEqual(200, response.status_code)

    def test_get_meal_with_meal_id(self):
        '''test client can get a specific meal using meal id only'''
        # login an admin user
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))

        # populate meals table
        meal = dict(name='Mukimo', price=100, description='Mt Kenya heritage')
        response = self.client.post(
            MEALS_URL, data=json.dumps(meal), headers=headers)
        url = '{}/1'.format(MEALS_URL)
        response = self.client.get(url, headers=headers)
        self.assertEqual(200, response.status_code)

    def test_only_admin_gets_all_meals(self):
        '''GET /apiv1/meals is reserved for admin only'''
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))

        response = self.client.get(MEALS_URL, headers=headers)
        self.assertEqual(401, response.status_code)
        expected = 'Unauthorized'
        self.assertEqual(json.loads(response.data)['message'], expected)

    def test_add_a_meal(self):
        '''test admin can add meals'''
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        meal = dict(
            name='Mukimo', price=100, description='Mt Kenya heritage')
        response = self.client.post(
            MEALS_URL, data=json.dumps(meal), headers=headers)
        self.assertEqual(201, response.status_code)
        expected = 'New meal created'
        self.assertEqual(expected, json.loads(response.data)['message'])

    def test_only_admin_can_add_meals(self):
        '''POST  to /api/v1/meals is a route reserverd for admin, normal users
        lack priviledges'''
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        meal_data = {
            'name': 'Muthokoi',
            'price': 90,
            'description': 'Kamba manenos'}
        response = self.client.post(
            MEALS_URL, data=json.dumps(meal_data), headers=headers)
        self.assertEqual(401, response.status_code)

    def test_delete_a_meal(self):
        '''test admin can delete a meal'''
        # add a meal
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        meal = dict(
            name='Mukimo',
            price=100,
            description='Mt Kenya heritage')
        response = self.client.post(
            MEALS_URL, data=json.dumps(meal), headers=headers)
        url = '{}/1'.format(MEALS_URL)
        response = self.client.delete(url, headers=headers)
        self.assertEqual(200, response.status_code)

    def test_only_admin_deletes_meals(self):
        '''test only user with admin rights can delete meals'''
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        self.create_meal()
        url = '{}/1'.format(MEALS_URL)
        response = self.client.delete(url, headers=headers)
        self.assertEqual(401, response.status_code)

    def test_edit_a_meal(self):
        '''test admin can edit a meal'''
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        meal = dict(name='Mukimo', price=100, description='Mt Kenya heritage')
        response = self.client.post(
            MEALS_URL, data=json.dumps(meal), headers=headers)
        data = {'new_data': {'price': 200}}
        
        url = '{}/1'.format(MEALS_URL)
        response = self.client.put(
            url, data=json.dumps(data), headers=headers)
        self.assertEqual(202, response.status_code)
        expected = 'Meal 1 edited'
        result = json.loads(response.data)['message']
        self.assertEqual(expected, result)

    def test_only_admin_can_edit_meals(self):
        '''test editing meals required admin rights'''
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        self.create_meal()
        new_data = {'price': 200}
        url = '{}/1'.format(MEALS_URL)
        response = self.client.put(url,data=new_data, headers=headers)
        self.assertEqual(401, response.status_code)
        expected = 'Unauthorized'
        result = json.loads(response.data)['message']
        self.assertEqual(expected, result)

    def test_get_unsaved_meal(self):
        '''test client can get a specific meal using meal id only'''
        # login an admin user
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))

        # populate meals table
        url = '{}/1'.format(MEALS_URL)
        response = self.client.get(url, headers=headers)
        self.assertEqual(404, response.status_code)
        self.assertEqual('Meal 1 not found', json.loads(response.data))
    
    def test_delete_unavailable_meal(self):
        '''Test attempt o delete unavailable meal returns 404'''
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))

        # populate meals table
        url = '{}/1'.format(MEALS_URL)
        response = self.client.delete(url, headers=headers)
        self.assertEqual(404, response.status_code)
        self.assertEqual('Meal 1 not found', json.loads(response.data))
    
    def test_add_meal_with_missing_details(self):
        '''test can not add meal with missing details'''
        invalid_name = {
            'name':'',
            'price':10,
            'description':'blah blah'}
        invalid_price = {
            'name':'Fish',
            'price':'l10',
            'description':'blah blah'}
        invalid_descr = {
            'name':'Fish',
            'price':10,
            'description':''}
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        # invalid name
        response = self.client.post(
            MEALS_URL, data=json.dumps(invalid_name), headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            'Invalid meal name provided', json.loads(response.data)['error'])
        # invalid price
        response = self.client.post(
            MEALS_URL, data=json.dumps(invalid_price), headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            'Invalid value for price', json.loads(response.data)['error'])
        # invalid description
        response = self.client.post(
            MEALS_URL, data=json.dumps(invalid_descr), headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            'Invalid description', json.loads(response.data)['error'])
