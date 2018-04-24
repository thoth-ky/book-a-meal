'''Tests for api endpoints'''
import json

# local imports
from . import BaseTestClass


class TestUserManagement(BaseTestClass):
    '''Test User registration and logging in and out'''
    def test_user_registration(self):
        '''test user can register'''
        # register user
        response = self.client.post('/vi/auth/signup', data=json.dumps(self.new_user))
        # check status code
        self.assertEqual(201, response.status_code)
        expected = {'message': 'Registration succesful, proceed to log in'}
        # check returned message
        self.assertEqual(expected, json.loads(response.data))

    def test_user_login(self):
        '''test user can login'''
        # register user
        response = self.client.post('/v1/auth/signup', data=json.dumps(
            self.new_user))
        # check user created succesfully
        self.assertEqual(201, response.status_code)
        # try login with right password
        correct_password = self.new_user['password']
        data = {'password': correct_password, 'email': self.new_user['email']}
        response = self.client.post('/v1/auth/signin', data=json.dumps(data))
        self.assertEqual(200, response.status_code)
        expected = {'message': 'Login succesful'}
        self.assertEqual(expected, json.loads(response.data))

    def test_login_with_wrong_password(self):
        '''test if user can log in with wrong password'''
        # register user
        response = self.client.post('/v1/auth/signup', data=json.dumps(
            self.new_user))
        # check user created succesfully
        self.assertEqual(201, response.status_code)
        wrong_passsword = 'wrongpassword'
        data = {'password': wrong_password, 'email': self.new_user['email']}
        response = self.client.post('/v1/auth/signin', data=json.dumps(data))
        self.assertEqual(401, response.status_code)
        expected = {'message': 'The email or password provided are incorrect. Please try again'}
        self.assertEqual(expected, json.loads(response.data))



class TestMealsManagement(BaseTestClass):
    def test_get_all_meals(self):
        '''test client can get al meals'''
        self.login_admin()
        response = self.client.get('/v1/meals')
        self.assertEqual(200, response.status_code)
        all_meals = self.Database.meals
        expected = {'message': 'succesful request',
                    'data': all_meals}
        self.assertEqual(expected, json.loads(response.data))

    def test_add_a_meal(self):
        '''test admin can add meals'''
        self.login_admin()
        response = client.post('/v1/meals', data=json.dumps(
            self.meal))
        self.assertEqual(201, response.status_code)
        expected = {'message': 'New meal created'}
        self.assertEqual(expected, json.loads('status_code'))

    def test_delete_a_meal(self):
        '''test admin can delete a meal'''
        # add a meal
        self.login_admin()
        response = client.post('/v1/meals', data=json.dumps(
            self.meal))
        self.assertEqual(201, response.status_code)
        meal_id = 1  # meal_id for meal to delete
        response = self.client.delete('vi/meals/{}'.format(meal_id))
        self.assertEqual(204, response.status_code)

    def test_edit_a_meal(self):
        '''test admin can edit a meal'''
        # add a meal
        self.login_admin()
        response = self.client.post('/v1/meals', data=json.dumps(
            self.meal))
        self.assertEqual(201, response.status_code)
        meal_id = 1  # meal_id for meal to edit
        new_data = {'price': 200}
        response = self.client.put('/v1/meals/{}'.format(meal_id), data=new_data)
        self.assertEqual(200, response.status_code)
        expected = {'message': 'Meal updated succesfully'}
        self.assertEqual(expected, json.loads(response.data))


class TestMenuManagement(BaseTestClass):
    def test_setup_menu(self):
        self.login_admin()
        meal1 = self.Meal(meal_id=1, name='Fish', price=100, description='Tasty Tilapia')
        meal2 = self.Meal(meal_id=2, name='Ugali', price=50, description='Tasty Ugali')
        self.Database.add(meal1)
        self.Database.add(meal2)
        menu = [meal1, meal2]
        response = self.client.post('/v1/menu', data =json.dumps(menu))
        self.assertEqual(200, response.status_code)
        expected = {'message': 'Menu created succesfully'}
        self.assertEqual(expected, json.loads(response.data))

    def test_get_menu(self):
        self.login_user()
        response = self.client.get('/v1/menu')
        menu = self.Database.current_menu
        self.assertEqual(200, response.status_code)
        expected = {'message': 'Menu request succesful',
                    'menu': menu}
        self.assertEqual(expected, json.loads(response.data))


class TestOrdersManagement(BaseTestClass):
    def test_make_orders(self):
        '''tetst authenticated users can make orders'''
        self.login_user()
        response = self.client.get('/v1/menu')
        self.assertEqual(200, response.status_code)
        current_menu = json.loads(response.data)['menu']
        meal_to_order = current_menu[0]
        data = {'meal': meal_to_order, 'quantity': 1}
        response = self.client.post('/v1/orders', data=json.dumps(data))
        self.assertEqual(201, response.status_code)
        expected = {'message': 'Order has been placed', 'order_id': 1}
        self.assertEqual(expected, json.loads(response.data))

    def test_edit_order(self):
        '''test authenticated users can edit orders'''
        self.login_user()
        response = self.client.get('/v1/menu')
        self.assertEqual(200, response.status_code)
        current_menu = json.loads(response.data)['menu']
        meal_to_order = current_menu[0]
        data = {'meal': meal_to_order, 'quantity': 1}
        # place order
        response = self.client.post('/v1/orders', data=json.dumps(data))
        self.assertEqual(201, response.status_code)
        order_id = json.loads(response.data)['order_id']
        new_order_data = {'quantity': 2}
        # put request to edit order
        response = self.client.put('/v1/orders/{}'.format(order_id), data=json.dumps(
            new_order_data))
        self.assertEqual(200, response.status_code)
        expected ={'message': 'Order modified succesfully'}
        self.assertEqual(expected, json.loads(response.data))

    def test_get_all_orders(self):
        '''test admin can get all orders'''
        self.login_admin()
        response = self.client.get('/v1/orders')
        self.assertEqual(200, response.status_code)
        expected = {'message': 'All Orders',
                    'orders': self.Database.orders}
        self.assertEqual(expected, json.loads(response.data))
