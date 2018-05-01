'''Tests for api endpoints'''
import json

# local imports
from . import BaseTestClass

SIGNUP_URL = '/api/v1/auth/signup'
SIGNIN_URL = '/api/v1/auth/signin'
MEALS_URL = '/api/v1/meals'
MENU_URL = 'api/v1/menu'
ORDERS_URL = 'api/v1/orders'


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
        self.create_meal()
        meal_id = 1
        url = MEALS_URL + '/{}'.format(meal_id)
        response = self.client.get(url, headers=headers)
        self.assertEqual(200, response.status_code)

    def test_only_admin_gets_all_meals(self):
        '''GET /v1/meals is reserved for admin only'''
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

        response = self.client.post(MEALS_URL, data=json.dumps(self.meal), headers=headers)
        self.assertEqual(201, response.status_code)
        expected = {'message': 'New meal created'}
        self.assertEqual(expected, json.loads(response.data))

    def test_only_admin_can_add_meals(self):
        '''POST  to /v1/meals is a route reserverd for admin, normal users
        lack priviledges'''
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))

        response = self.client.post(MEALS_URL, data=json.dumps(
            self.meal), headers=headers)
        self.assertEqual(401, response.status_code)

    def test_delete_a_meal(self):
        '''test admin can delete a meal'''
        # add a meal
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        self.create_meal()
        meal_id = 1  # meal_id for meal to delete
        url = MEALS_URL + '/1'
        response = self.client.delete(url, headers=headers)
        self.assertEqual(200, response.status_code)

    def test_only_admin_deletes_meals(self):
        '''test only user with admin rights can delete meals'''
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        self.create_meal()
        meal_id = 1  # meal_id for meal to delete
        url = MEALS_URL + '/1'
        response = self.client.delete(url, headers=headers)
        self.assertEqual(401, response.status_code)

    def test_edit_a_meal(self):
        '''test admin can edit a meal'''
        # add a meal
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        
        response = self.client.post(MEALS_URL, data=json.dumps(self.meal2), headers=headers)
        meal_id = self.meal2['meal_id']  # meal_id for meal to edit
        data = {'new_data': {'price': 200}}
        url = MEALS_URL + '/{}'.format(meal_id)
        response = self.client.put(url, data=json.dumps(data), headers=headers)
        self.assertEqual(202, response.status_code)
        expected = 'Meal {} edited'.format(meal_id)
        result = json.loads(response.data)['message']
        self.assertEqual(expected, result)

    def test_only_admin_can_edit_meals(self):
        '''test editing meals required admin rights'''
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        self.create_meal()
        meal_id = 1  # meal_id for meal to edit
        new_data = {'price': 200}
        url =MEALS_URL + '/{}'.format(meal_id)
        response = self.client.put(url,data=new_data, headers=headers)
        self.assertEqual(401, response.status_code)
        expected = 'Unauthorized'
        result = json.loads(response.data)['message']
        self.assertEqual(expected, result)

