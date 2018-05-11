'''Tests for api endpoints'''
import json
from datetime import datetime
# local imports
from . import BaseTestClass

MENU_URL = '/api/v1/menu'


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
        expected = 'Menu created successfully'
        self.assertEqual(expected, json.loads(response.data)['message'])

    def test_setup_menu_for_a_date(self):
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        
        self.meal1.save()
        menu = {'meal_list': [self.meal1.meal_id], 'date': '12-4-2018'}
        
        response = self.client.post(MENU_URL, data=json.dumps(menu), headers=headers)
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
        response = self.client.post(MENU_URL, data=json.dumps(menu), headers=headers)
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
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        
        self.meal1.save()
        self.meal2.save()
        # use invalid meal_list
        menu = {'meal_list': self.meal1.meal_id}
        res = self.client.post(MENU_URL, data=json.dumps(menu), headers=headers)
        self.assertEqual(400, res.status_code)
        self.assertEqual('Make meal_list a list of Meal object IDs', json.loads(res.data)['error'])
        # use invalid date
        menu = {'meal_list': [self.meal1.meal_id], 'date':'2018-04-20'}
        res = self.client.post(MENU_URL, data=json.dumps(menu), headers=headers)
        self.assertEqual(400, res.status_code)
        self.assertEqual('Ensure date is provided using format DD-MM-YYYY', json.loads(res.data)['error'])
 
    def test_can_not_add_empty_menu(self):
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        data = {}
        response = self.client.post(MENU_URL, data=json.dumps(data), headers=headers)
        self.assertEqual(202, response.status_code)
        expected = 'Menu object can not be empty'
        self.assertEqual(expected, json.loads(response.data)['message'])
    
    def test_returns_404_when_no_menu(self):
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        response = self.client.get(MENU_URL, headers=headers)
        self.assertEqual(404, response.status_code)
        today = datetime.utcnow().date()
        today = datetime(year=today.year, month=today.month, day=today.day)
        self.assertEqual('No menu found for {}'.format(today.ctime()), json.loads(response.data))
    
    def test_can_not_post_with_invalid_meal_ids(self):
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        
        menu = {'meal_list': [1]}
        response = self.client.post(MENU_URL, data=json.dumps(menu), headers=headers)
        self.assertEqual(202, response.status_code)
        self.assertEqual(json.loads(response.data), 'Invalid meal_id 1')
