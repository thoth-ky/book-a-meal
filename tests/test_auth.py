'''Tests for api endpoints'''
import json

# local imports
from . import BaseTestClass

SIGNUP_URL = '/api/v1/auth/signup'
SIGNIN_URL = '/api/v1/auth/signin'
MEALS_URL = '/api/v1/meals'
MENU_URL = 'api/v1/menu'
ORDERS_URL = 'api/v1/orders'


class TestUserManagement(BaseTestClass):
    '''Test User registration and logging in and out'''
    def test_user_registration(self):
        '''test user can register'''
        # register user
        new_user = dict(username='eve', email='eve@m.c', password='eve123')
        response = self.client.post(SIGNUP_URL, data=json.dumps(new_user))
        # check status code
        self.assertEqual(201, response.status_code)
        expected = {'message': 'User registration succesful, proceed to login'}
        # check returned message
        self.assertEqual(expected, json.loads(response.data))

    def test_can_register_admin(self):
        '''tests ana dmin can be registered'''
        response = self.client.post(SIGNUP_URL, data=json.dumps(self.admin_user))
        # check status code
        self.assertEqual(201, response.status_code)
        expected = {
            'message': 'Admin registration succesful, proceed to login'
        }
        # check returned message
        self.assertEqual(expected, json.loads(response.data))

    def test_can_not_register_same_user_twice(self):
        '''test registering same user twice raises error'''
        response = self.client.post(SIGNUP_URL, data=json.dumps(self.new_user))
        # check status code
        self.assertEqual(201, response.status_code)
        response = self.client.post(SIGNUP_URL, data=json.dumps(self.new_user))
        self.assertEqual(202, response.status_code)
        expected = 'User already exists'
        result = json.loads(response.data)['message']
        self.assertEqual(expected, result)

    def test_user_login(self):
        '''test user can login'''
        # register user
        response = self.client.post(SIGNUP_URL, data=json.dumps(self.new_user))
        # check status code
        self.assertEqual(201, response.status_code)
        # try login with right password
        correct_password = self.new_user['password']
        data = {'password': correct_password, 'email': self.new_user['email']}
        response = self.client.post(SIGNIN_URL, data=json.dumps(data))
        # self.assertEqual(200, response.status_code)
        access_token = json.loads(response.data)['access_token']
        self.assertTrue(access_token)
        message = json.loads(response.data)['message']
        expected = 'Successfully logged in'
        self.assertEqual(expected, message)

    def test_login_with_wrong_password(self):
        '''test if user can log in with wrong password'''
        wrong_password = 'wrongpassword'
        data = {'password': wrong_password, 'email': self.new_user['email']}
        response = self.client.post(SIGNIN_URL, data=json.dumps(data))
        self.assertEqual(401, response.status_code)
        expected = {
            'message': 'The username/email or password provided is not correct'
        }
        self.assertEqual(expected, json.loads(response.data))

