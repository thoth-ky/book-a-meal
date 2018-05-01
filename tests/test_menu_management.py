'''Tests for api endpoints'''
import json

# local imports
from . import BaseTestClass

SIGNUP_URL = '/api/v1/auth/signup'
SIGNIN_URL = '/api/v1/auth/signin'
MEALS_URL = '/api/v1/meals'
MENU_URL = 'api/v1/menu'
ORDERS_URL = 'api/v1/orders'


class TestMenuManagement(BaseTestClass):
    '''tests for menu resource'''
    def test_setup_menu(self):
        '''test admin can set up menu'''
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
        self.assertEqual(201, response.status_code)
        expected = {'message': 'Menu created successfully'}
        self.assertEqual(expected, json.loads(response.data))

    def test_only_admin_can_setup_menu(self):
        '''test normal user can't create menu'''
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))

        menu = {'meal_list': ['dummy data']}
        response = self.client.post(MENU_URL, data=json.dumps(menu), headers=headers)
        self.assertEqual(401, response.status_code)

    def test_get_menu(self):
        '''Test users can get menu'''
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        
        response = self.client.get(MENU_URL, headers=headers)
        menu = self.database.current_menu
        menu = [menu[item] for item in menu]
        self.assertEqual(200, response.status_code)
        expected = {'message': 'Menu request succesful',
                    'menu': menu}
        self.assertEqual(expected, json.loads(response.data))

