'''Tests for api endpoints'''
import json
from datetime import datetime
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
        
        self.meal1.save()
        self.meal2.save()
        menu = {'meal_list': [self.meal1.meal_id, self.meal2.meal_id]}
        
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
        
        self.meal1.now_available()
        self.meal2.now_available()
        self.menu.save()
        self.menu.add_meal(self.meal1)
        
        response = self.client.get(MENU_URL, headers=headers)
        date = datetime.utcnow().date()
        menu = self.menu_model.query.filter_by(date=date).first()
        menu = [item.make_dict() for item in menu.meals]
        self.assertEqual(200, response.status_code)
        expected = {'message': 'Menu request succesful',
                    'menu': menu}
        self.assertEqual(expected, json.loads(response.data))

