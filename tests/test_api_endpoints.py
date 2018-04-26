'''Tests for api endpoints'''
import json

# local imports
from . import BaseTestClass


class TestUserManagement(BaseTestClass):
    '''Test User registration and logging in and out'''
    def test_user_registration(self):
        '''test user can register'''
        # register user
        new_user = dict(username='eve', email='eve@m.c', password='eve123')
        response = self.client.post(
            '/v1/auth/signup', data=json.dumps(new_user))
        # check status code
        self.assertEqual(201, response.status_code)
        expected = {'message': 'User registration succesful, proceed to login'}
        # check returned message

        self.assertEqual(expected, json.loads(response.data))

    def test_can_register_admin(self):
        '''tests ana dmin can be registered'''
        response = self.client.post(
            '/v1/auth/signup', data=json.dumps(self.admin_user))
        # check status code
        self.assertEqual(201, response.status_code)
        expected = {
            'message': 'Admin registration succesful, proceed to login'
        }
        # check returned message
        self.assertEqual(expected, json.loads(response.data))

    def test_cant_register_same_user_twice(self):
        response = self.client.post(
            '/v1/auth/signup', data=json.dumps(self.new_user))
        # check status code
        self.assertEqual(201, response.status_code)
        response = self.client.post(
            '/v1/auth/signup', data=json.dumps(self.new_user))
        self.assertEqual(202, response.status_code)
        expected = 'User already exists'
        result = json.loads(response.data)['message']
        self.assertEqual(expected, result)

    def test_user_login(self):
        '''test user can login'''
        # register user
        response = self.client.post(
            '/v1/auth/signup', data=json.dumps(self.new_user))
        # check status code
        self.assertEqual(201, response.status_code)
        # try login with right password
        correct_password = self.new_user['password']
        data = {'password': correct_password, 'email': self.new_user['email']}
        response = self.client.post('/v1/auth/signin', data=json.dumps(data))
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
        response = self.client.post('/v1/auth/signin', data=json.dumps(data))
        self.assertEqual(401, response.status_code)
        expected = {
            'message': 'The username/email or password provided is not correct'
        }
        self.assertEqual(expected, json.loads(response.data))


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
        response = self.client.get('/v1/meals/', headers=headers)
        self.assertEqual(200, response.status_code)
        # correct database concurrency
        # all_meals = self.Database.meals
        # expected = {'message': 'succesful request',
        #             'data': all_meals}
        # self.assertEqual(expected, json.loads(response.data))

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
        response = self.client.get('/v1/meals/{}/'.format(meal_id), headers=headers)
        self.assertEqual(200, response.status_code)
        expected = self.Database.meals[str(meal_id)]
    #     result = json.loads(response.data)['meal']
    #     self.assertEqual(expected, result)

    def test_only_admin_can_get_all_meals(self):
        '''GET /v1/meals is reserved for admin only'''
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))

        response = self.client.get('/v1/meals', headers=headers)
        self.assertEqual(401, response.status_code)
        expected = 'Unauthorized'
        self.assertEqual(json.loads(response.data)['message'], expected)

    def test_add_a_meal(self):
        '''test admin can add meals'''
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))

        response = self.client.post('/v1/meals', data=json.dumps(self.meal), headers=headers)
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

        response = self.client.post('/v1/meals', data=json.dumps(
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
        response = self.client.delete('/v1/meals/{}/'.format(meal_id), headers=headers)
        self.assertEqual(200, response.status_code)

    def test_only_admin_deletes_meals(self):
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        self.create_meal()
        meal_id = 1  # meal_id for meal to delete
        response = self.client.delete('/v1/meals/{}/'.format(meal_id), headers=headers)
        self.assertEqual(401, response.status_code)

    def test_edit_a_meal(self):
        '''test admin can edit a meal'''
        # add a meal
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        
        response = self.client.post('/v1/meals', data=json.dumps(self.meal2), headers=headers)
        meal_id = self.meal2['meal_id']  # meal_id for meal to edit
        data = {'new_data': {'price': 200}}
        response = self.client.put(
            '/v1/meals/{}/'.format(meal_id), data=json.dumps(data), headers=headers)
        self.assertEqual(202, response.status_code)
        expected = 'Meal {} edited'.format(meal_id)
        result = json.loads(response.data)['message']
        self.assertEqual(expected, result)

    def test_only_admin_can_edit_meals(self):
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        self.create_meal()
        meal_id = 1  # meal_id for meal to edit
        new_data = {'price': 200}
        
        response = self.client.put(
            '/v1/meals/{}/'.format(meal_id), data=new_data, headers=headers)
        self.assertEqual(401, response.status_code)
        expected = 'Unauthorized'
        result = json.loads(response.data)['message']
        self.assertEqual(expected, result)


class TestMenuManagement(BaseTestClass):
    '''tests for menu resource'''
    def test_setup_menu(self):
        '''test admin can set up menu'''
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        
        meal1 = self.Meal(
            meal_id=1, name='Fish', price=100, description='Tasty Tilapia')
        meal2 = self.Meal(
            meal_id=2, name='Ugali', price=50, description='Tasty Ugali')
        self.Database.add(meal1)
        self.Database.add(meal2)

        # serialize 
        meal1 = meal1.make_dict()
        meal2 = meal2.make_dict()
        menu = {'meal_list': [meal1, meal2]}
        
        response = self.client.post('/v1/menu', data=json.dumps(menu), headers=headers)
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
        response = self.client.post('/v1/menu', data=json.dumps(menu), headers=headers)
        self.assertEqual(401, response.status_code)

    def test_get_menu(self):
        '''Test users can get menu'''
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        
        response = self.client.get('/v1/menu', headers=headers)
        menu = self.Database.current_menu
        menu = [menu[item] for item in menu]
        self.assertEqual(200, response.status_code)
        expected = {'message': 'Menu request succesful',
                    'menu': menu}
        self.assertEqual(expected, json.loads(response.data))


class TestOrdersManagement(BaseTestClass):
    '''Tests for OrderResource '''
    def setup_menu(self):
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        
        meal1 = self.Meal(
            meal_id=1, name='Fish', price=100, description='Tasty Tilapia')
        meal2 = self.Meal(
            meal_id=2, name='Ugali', price=50, description='Tasty Ugali')
        self.Database.add(meal1)
        self.Database.add(meal2)

        # serialize 
        meal1 = meal1.make_dict()
        meal2 = meal2.make_dict()
        menu = {'meal_list': [meal1, meal2]}
        
        response = self.client.post('/v1/menu', data=json.dumps(menu), headers=headers)
        return response

    def test_make_orders(self):
        '''tetst authenticated users can make orders'''
        res = self.setup_menu()
        self.assertEqual(201, res.status_code)

        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        response = self.client.get('/v1/menu', headers=headers)
        self.assertEqual(200, response.status_code)
        current_menu = json.loads(response.data)['menu']
        meal_to_order = current_menu[0]
        data = {'order_id': 1, 'meal': meal_to_order, 'quantity': 1}
        
        response = self.client.post('/v1/orders', data=json.dumps(data), headers=headers)
        self.assertEqual(201, response.status_code)
        expected = 'Order has been placed'
        self.assertEqual(expected, json.loads(response.data)['message'])

    def test_edit_order(self):
        '''test authenticated users can edit orders'''
        res = self.setup_menu()
        self.assertEqual(201, res.status_code)

        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        # get menu
        response = self.client.get('/v1/menu', headers=headers)
        self.assertEqual(200, response.status_code)
        current_menu = json.loads(response.data)['menu']
        meal_to_order = current_menu[0]
        data = {'order_id': 2, 'meal': meal_to_order, 'quantity': 1}
        # place order
        response = self.client.post('/v1/orders/', data=json.dumps(data), headers=headers)
        self.assertEqual(201, response.status_code)
        order = json.loads(response.data)['order']
        order_id = order.get('order_id')
        
        # put request to edit order
        data = {'new_data': {'quantity': 2}}
        response = self.client.put('/v1/orders/{}'.format(order_id), data=json.dumps(data), headers=headers)
        self.assertEqual(200, response.status_code)
        expected = {'message': 'Order modified succesfully'}
        self.assertEqual(expected, json.loads(response.data))

    def test_get_all_orders(self):
        '''test admin can get all orders'''
        res = self.login_admin()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))
        response = self.client.get('/v1/orders', headers=headers)
        self.assertEqual(200, response.status_code)
        orders = self.Database.orders
        orders = [orders[item].make_dict() for item in orders]
        expected = {'message': 'All Orders',
                    'orders': orders}
        self.assertEqual(expected, json.loads(response.data))

    def test_user_only_get_own_orders(self):
        '''test only admin can access orders'''
        # res = self.login_user(username='eve', password='eve123')
        res = self.login_user()
        self.assertEqual(200, res.status_code)
        access_token = json.loads(res.data)['access_token']
        headers = dict(Authorization='Bearer {}'.format(access_token))

        response = self.client.get('/v1/orders', headers=headers)
        self.assertEqual(200, response.status_code)
        orders = self.Database.user_orders
        orders = [orders[item].make_dict() for item in orders]
        expected = {'message': 'All Orders',
                    'orders': orders}
        self.assertEqual(expected, json.loads(response.data))
