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
        # test_user = dict(username='eve', email='eve@mail.com', password='eve1234')
        response = self.client.post(SIGNUP_URL, data=json.dumps(self.test_user))
        # check status code
        self.assertEqual(201, response.status_code)
        expected = {'message': 'User registration succesful, proceed to login'}
        # check returned message
        self.assertEqual(expected, json.loads(response.data))

    def test_can_register_admin(self):
        '''tests ana dmin can be registered'''
        response = self.client.post(SIGNUP_URL, data=json.dumps(self.admin_user))
        # check status code
        # self.assertEqual(201, response.status_code)
        expected = {
            'message': 'Admin registration succesful, proceed to login'
        }
        # check returned message
        self.assertEqual(expected, json.loads(response.data))

    def test_can_not_register_same_user_twice(self):
        '''test registering same user twice raises error'''
        response = self.client.post(SIGNUP_URL, data=json.dumps(self.test_user))
        # check status code
        self.assertEqual(201, response.status_code)
        response = self.client.post(SIGNUP_URL, data=json.dumps(self.test_user))
        self.assertEqual(202, response.status_code)
        expected = 'Username or Email not available.'
        result = json.loads(response.data)['message']
        self.assertEqual(expected, result)

    def test_user_login(self):
        '''test user can login'''
        # register user
        response = self.client.post(SIGNUP_URL, data=json.dumps(self.test_user))
        # check status code
        self.assertEqual(201, response.status_code)
        # try login with right password
        correct_password = self.test_user['password']
        data = {'password': correct_password, 'email': self.test_user['email']}
        response = self.client.post(SIGNIN_URL, data=json.dumps(data))
        self.assertEqual(200, response.status_code)
        access_token = json.loads(response.data)['access_token']
        self.assertTrue(access_token)
        message = json.loads(response.data)['message']
        expected = 'Successfully logged in'
        self.assertEqual(expected, message)

    def test_login_with_wrong_password(self):
        '''test if user can log in with wrong password'''
        wrong_password = 'wrongpassword'
        data = {'password': wrong_password, 'email': self.test_user['email']}
        response = self.client.post(SIGNIN_URL, data=json.dumps(data))
        self.assertEqual(401, response.status_code)
        expected = {
            'message': 'The username/email or password provided is not correct'
        }
        self.assertEqual(expected, json.loads(response.data))

    def test_login_non_existent_user(self):
        data = {'password':'password', 'username':'beverly'}
        response = self.client.post(SIGNIN_URL, data=json.dumps(data))
        self.assertEqual(401, response.status_code)
        expected = {
            'message': 'The username/email or password provided is not correct'
        }
        self.assertEqual(expected, json.loads(response.data))

    def test_signup_with_invalid_details(self):
        invalid_email = {'username': 'jujuju', 'email': 'notemail', 'password': 'password'}
        res = self.client.post(SIGNUP_URL, data=json.dumps(invalid_email))
        self.assertEqual(400, res.status_code)
        self.assertEqual('Invalid Email', json.loads(res.data)['ERR'])
        invalid_password = {'username':'user', 'email':'user@gmail.com', 'password':'qwr'}
        res = self.client.post(SIGNUP_URL, data=json.dumps(invalid_password))
        self.assertEqual(400, res.status_code)
        self.assertEqual('Invalid password. Ensure password is a string of not less than 8 characters', json.loads(res.data)['ERR'])
        invalid_username = {'username':"a", 'email':'user@gmail.com', 'password':'password1'}
        res = self.client.post(SIGNUP_URL, data=json.dumps(invalid_username))
        self.assertEqual(400, res.status_code)
        self.assertEqual('Invalid username. Ensure username has more than 3 characters', json.loads(res.data)['ERR'])

    def test_login_with_invalid_details(self):
        invalid_username = {'username':'ku', 'password':'password'}
        invalid_email = {'email':'notemail', 'password':'password'}
        res = self.client.post(SIGNIN_URL, data=json.dumps(invalid_username))
        self.assertEqual(400, res.status_code)
        res = self.client.post(SIGNIN_URL, data=json.dumps(invalid_email))
        self.assertEqual(400, res.status_code)
        