'''This contains a a basetest case'''

from unittest import TestCase
import json
# local imports
try:
    from app import create_app
    from app.models import Database, Meal, User, Menu, Admin, Order
except ModuleNotFoundError:
    from .app import create_app
    from .app.models import Database, Meal, User, Menu, Admin, Order


class BaseTestClass(TestCase):
    '''An abstract base class for tests, contains
    all common variables methods'''

    def setUp(self):
        self.maxDiff = None
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.new_user = {'username': 'john', 'email': 'john@mail.com',
                         'password': 'password'}
        self.admin_user = {'username': 'admin', 'email': 'admin@mail.com',
                         'password': 'password', 'admin': True}
        self.Database = Database()
        self.Meal = Meal
        self.Order = Order
        self.Menu = Menu
        self.Order = Order
        self.User = User
        self.Admin = Admin
        self.meal = {'meal_id': 1, 'name': 'Fish', 'price': 100, 'description': 'Tasty Tilapia'}

    def login_user(self):
        # register user
        self.client.post('/v1/auth/signup', data=json.dumps(self.new_user))
        data = {'password': self.new_user['password'], 'email': self.new_user['email']}
        self.client.post('v1/auth/signin', data=json.dumps(data))

    def login_admin(self):
        self.client.post('/v1/auth/signup', data=json.dumps(self.admin_user))
        data = {'password': self.new_user['password'], 'email': self.admin_user['email']}
        self.client.post('v1/auth/signin', data=json.dumps(data))

    def create_meal(self):
        meal = self.Meal(meal_id=1, name='Fish', price=100, description='Tasty Tilapia')
        self.Database.add(meal)

    def tearDown(self):
        # reset all database list to empty lists
        self.Database.meals = []
        self.Database.admins = []
        self.Database.users = []
        self.Database.current_menu = []
        self.Database.orders = []