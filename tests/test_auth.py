'''Tests for api endpoints'''
import json

# local imports
from . import BaseTestClass

SIGNUP_URL = '/api/v2/auth/signup'
SIGNIN_URL = '/api/v2/auth/signin'
LOGOUT_URL = '/api/v2/logout'
MEALS_URL = '/api/v2/meals'
MENU_URL = '/api/v2/menu'
ORDERS_URL = '/api/v2/orders'
USERS_URL = '/api/v2/users'
ACC_URL = '/api/v2/users/1'
ACC_URL2 = '/api/v2/users/100'


class TestUserManagement(BaseTestClass):
    '''Test User registration and logging in and out'''
    def test_user_registration(self):
        '''test user can register'''
        response = self.client.post(
            SIGNUP_URL, data=json.dumps(self.test_user))
        # check status code
        self.assertEqual(201, response.status_code)
        expected = '''User registration succesful, and logged in. Your access token is'''
        # check returned message
        result = json.loads(response.data)
        self.assertEqual(expected, result['message'])
        self.assertTrue(result['access_token'])

    def test_can_not_register_same_user_twice(self):
        '''test registering same user twice raises error'''
        response = self.client.post(
            SIGNUP_URL, data=json.dumps(self.test_user))
        # check status code
        self.assertEqual(201, response.status_code)
        response = self.client.post(
            SIGNUP_URL, data=json.dumps(self.test_user))
        self.assertEqual(202, response.status_code)
        expected = 'Username or Email not available.'
        result = json.loads(response.data)['message']
        self.assertEqual(expected, result)

    def test_user_login(self):
        '''test user can login'''
        # register user
        response = self.client.post(
            SIGNUP_URL, data=json.dumps(self.test_user))
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
        data = {
            'password': wrong_password,
            'email': self.test_user['email']}
        response = self.client.post(
            SIGNIN_URL, data=json.dumps(data))
        self.assertEqual(401, response.status_code)
        expected = {
            'message': 'The username/email or password provided is not correct'
        }
        self.assertEqual(expected, json.loads(response.data))

    def test_login_non_existent_user(self):
        '''test non registered users can not log in'''
        data = {'password':'password', 'username':'beverly'}
        response = self.client.post(SIGNIN_URL, data=json.dumps(data))
        self.assertEqual(401, response.status_code)
        expected = {
            'message': 'The username/email or password provided is not correct'
        }
        self.assertEqual(expected, json.loads(response.data))

    def test_signup_with_invalid_details(self):
        '''test user signup using invalid details'''
        invalid_email = {
            'username': 'jujuju',
            'email': 'notemail',
            'password': 'password'}
        res = self.client.post(SIGNUP_URL, data=json.dumps(invalid_email))
        self.assertEqual(400, res.status_code)
        self.assertEqual('Invalid Email. Ensure email is valid and is of form "example@mail.com"', json.loads(res.data)['ERR'])
        invalid_password = {
            'username':'user',
            'email':'user@gmail.com',
            'password':'qwr'}
        res = self.client.post(
            SIGNUP_URL, data=json.dumps(invalid_password))
        self.assertEqual(400, res.status_code)
        self.assertEqual(
            'Invalid password. Ensure password is a string of not less than 8 characters', json.loads(res.data)['ERR'])
        invalid_username = {
            'username':"a",
            'email':'user@gmail.com',
            'password':'password1'}
        res = self.client.post(
            SIGNUP_URL, data=json.dumps(invalid_username))
        self.assertEqual(400, res.status_code)
        self.assertEqual(
            'Invalid username. Ensure username has more than 3 characters',
            json.loads(res.data)['ERR'])
        incomplete_details = {'username': None, 'email': '', 'password': None}
        res = self.client.post(SIGNUP_URL, data=json.dumps(incomplete_details))
        self.assertEqual(400, res.status_code)
        self.assertEqual('Incomplete details', json.loads(res.data)['ERR'])

    def test_login_with_invalid_details(self):
        '''test login with invalid details'''
        invalid_username = {'username':'ku', 'password':'password'}
        invalid_email = {'email':'notemail', 'password':'password'}
        res = self.client.post(SIGNIN_URL, data=json.dumps(invalid_username))
        self.assertEqual(400, res.status_code)
        res = self.client.post(SIGNIN_URL, data=json.dumps(invalid_email))
        self.assertEqual(400, res.status_code)
    
    def test_super_admin_functions(self):
        '''test super admin functionalities'''
        access_token = self.login_super_admin()
        headers = dict(Authorization='Bearer {}'.format(access_token))
        # create user
        self.create_user()
        # test superadmin can get a list of all users
        res = self.client.get(USERS_URL, headers=headers)
        users = self.user_model.get_all()
        users = [user.view() for user in users]
        self.assertEqual(users, json.loads(res.data)['users'])
        
        # test superadmin can get specific user
        res = self.client.get(ACC_URL, headers=headers)
        user = [self.user_model.get(user_id=1).view()]
        self.assertEqual(200, res.status_code)
        self.assertEqual(user, json.loads(res.data)['users'])
        # test get non existent user
        res = self.client.get(ACC_URL2, headers=headers)
        self.assertEqual(404, res.status_code)

        # promote user to admin
        res = self.client.put('/api/v2/users/promote/1', headers=headers)
        self.assertEqual(200, res.status_code)
        user = self.user_model.get(user_id=1)
        result = json.loads(res.data)
        self.assertEqual(user.view(), result['user'])
        self.assertEqual('User has now been made admin', result['message'])
        
        # delete user
        res = self.client.delete(ACC_URL, headers=headers)
        self.assertEqual(200, res.status_code)
        self.assertEqual(
            'User 1 has been deactivated', json.loads(res.data)['message'])
        
        # delete non existent user
        res = self.client.delete(ACC_URL, headers=headers)
        self.assertEqual(404, res.status_code)
        self.assertEqual(
            'User 1 does not exist', json.loads(res.data)['message'])

    def test_use_of_invalid_token(self):
        '''Test if user gives invalid token access could be gained'''
        invalid_token = 'invalid-access_token'
        headers = dict(Authorization='Bearer {}'.format(invalid_token))
        expected = 'Authorization Token not found or invalid!'
        
        # test admin functionality
        res = self.client.post(MEALS_URL, headers=headers)
        self.assertEqual(401, res.status_code)
        self.assertEqual(expected, json.loads(res.data)['error'])
        
        # test superadmin function
        res = self.client.get(USERS_URL, headers=headers)
        self.assertEqual(401, res.status_code)
        self.assertEqual(expected, json.loads(res.data)['error'])
        
        # test normal user function
        res = self.client.get(MENU_URL, headers=headers)
        self.assertEqual(401, res.status_code)
        self.assertEqual(expected, json.loads(res.data)['error'])

    def test_only_superuser_can_access_users_list(self):
        '''test super_admin_required deccorator works'''
        self.user1.save()
        token = self.user1.generate_token().decode()
        headers =dict(Authorization='Bearer {}'.format(token))
        res = self.client.get(USERS_URL, headers=headers)
        self.assertEqual(401, res.status_code)
        self.assertEqual('Unauthorized', json.loads(res.data)['message'])

    def test_users_can_logout(self):
        '''test users can logout'''
        self.user1.save()
        token = self.user1.generate_token().decode()
        headers =dict(Authorization=f'Bearer {token}')
        res = self.client.get(LOGOUT_URL, headers=headers)
        expected = f'{self.user1.username} has been logged out successfully.'
        self.assertEqual(200, res.status_code)
        self.assertEqual(expected, json.loads(res.data)['message'])

    def test_revoked_tokens_cannot_be_used(self):
        '''test returns 401  if user uses revoked tokens'''
        self.user1.save()
        token = self.user1.generate_token().decode()
        headers =dict(Authorization=f'Bearer {token}')
        res = self.client.get(LOGOUT_URL, headers=headers)
        self.assertEqual(200, res.status_code)
        res = self.client.get(MENU_URL, headers=headers)
        self.assertEqual(401, res.status_code)
        expected = 'Authorization Token not found or invalid!'
        self.assertEqual(expected, json.loads(res.data)['error'])
