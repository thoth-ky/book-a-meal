'''Tests for api endpoints'''
import json
from datetime import datetime
# local imports
from . import BaseTestClass

MENU_URL = '/api/v2/menu'
SIGNIN_URL = '/api/v2/auth/signin'


class TestMenuManagement(BaseTestClass):
    '''tests for menu resource'''
    def create_meals(self):
        admin = self.user_model(
            username='admin1', email='admin1@bam.com', password='admin1234')
        admin.admin = True
        admin.save()
        self.meal1.user_id = admin.user_id
        self.meal2.user_id = admin.user_id
        self.meal1.save()
        self.meal2.save()

    def test_setup_menu(self):
        '''test admin can set up menu'''
        self.create_meals()
        creds = dict(username='admin1', password='admin1234')
        res = self.client.post(SIGNIN_URL, data=json.dumps(creds))
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        
        menu = {'meal_list': [self.meal1.meal_id, self.meal2.meal_id]}
        
        response = self.client.post(
            MENU_URL, data=json.dumps(menu), headers=headers)
        self.assertEqual(201, response.status_code)
        expected = 'Menu created successfully'
        self.assertEqual(expected, json.loads(response.data)['message'])

    def test_setup_menu_for_a_date(self):
        '''test admin can create menu for specific dates'''
        self.create_meals()
        creds = dict(username='admin1', password='admin1234')
        res = self.client.post(SIGNIN_URL, data=json.dumps(creds))
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        
        menu = {'meal_list': [self.meal1.meal_id], 'date': '12-4-2018'}
        
        response = self.client.post(
            MENU_URL, data=json.dumps(menu), headers=headers)
        self.assertEqual(201, response.status_code)
        expected = 'Menu created successfully'
        self.assertEqual(expected, json.loads(response.data)['message'])

    def test_only_admin_can_setup_menu(self):
        '''test normal user can't create menu'''
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        

        menu = {'meal_list': ['dummy data']}
        response = self.client.post(
            MENU_URL, data=json.dumps(menu), headers=headers)
        self.assertEqual(401, response.status_code)

    def test_get_menu(self):
        '''Test users can get menu'''
        self.meal1.save()
        self.meal2.save()
        self.menu.add_meal(meal=[self.meal1, self.meal2], date=self.today)
        self.menu.save()
        menu = self.menu_model.get_all()[-1]
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        response = self.client.get(MENU_URL, headers=headers)
        
        self.assertEqual(200, response.status_code)
        expected = {'message': 'Menu request succesful',
                    'menu': menu.view()}
        self.assertEqual(expected, json.loads(response.data))

    def test_menu_setup_with_invalid_data(self):
        '''test users cannot create menu with invalid data'''
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        
        self.meal1.save()
        self.meal2.save()
        # use invalid meal_list
        menu = {'meal_list': self.meal1.meal_id}
        res = self.client.post(
            MENU_URL, data=json.dumps(menu), headers=headers)
        self.assertEqual(400, res.status_code)
        self.assertEqual(
            'Make meal_list a list of Meal object IDs',
            json.loads(res.data)['error'])
        # use invalid date
        menu = {'meal_list': [self.meal1.meal_id], 'date':'2018-04-20'}
        res = self.client.post(
            MENU_URL, data=json.dumps(menu), headers=headers)
        self.assertEqual(400, res.status_code)
        self.assertEqual(
            'Ensure date is provided using format DD-MM-YYYY',
            json.loads(res.data)['error'])
 
    def test_can_not_add_empty_menu(self):
        '''test cannot add empty menu items'''
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        data = {'meal_list':[]}
        response = self.client.post(
            MENU_URL, data=json.dumps(data), headers=headers)
        self.assertEqual(202, response.status_code)
        expected = 'Menu object can not be empty'
        self.assertEqual(expected, json.loads(response.data)['message'])
    
    def test_returns_404_when_no_menu(self):
        '''test when no menu to return http code 404 is returned'''
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        response = self.client.get(MENU_URL, headers=headers)
        self.assertEqual(404, response.status_code)
        today = datetime.utcnow().date()
        today = datetime(year=today.year, month=today.month, day=today.day)
        self.assertEqual(
            'No menu found for {}'.format(today.ctime()),
            json.loads(response.data)['message'])
    
    def test_can_not_post_with_invalid_meal_ids(self):
        '''test only meals with valid meal ids can be posted in menu'''
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        
        menu = {'meal_list': [1]}
        response = self.client.post(
            MENU_URL, data=json.dumps(menu), headers=headers)
        self.assertEqual(202, response.status_code)
        self.assertEqual(
            json.loads(response.data)['message'],
            'Menu object can not be empty')
