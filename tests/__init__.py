'''This contains a a basetest case'''
from datetime import datetime
from unittest import TestCase
import json
# local imports
try:
    from app import create_app, DB
    from app.models.models import Meal, User, Order, Menu
except ModuleNotFoundError:
    from ..app import create_app, DB
    from ..app.models.models import Meal, User, Order, Menu

SIGNUP_URL = '/api/v1/auth/signup'
SIGNIN_URL = '/api/v1/auth/signin'


class BaseTestClass(TestCase):
    '''An abstract base class for tests, contains
    all common variables methods'''

    def setUp(self):
        self.maxDiff = None
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.database = DB
        DB.drop_all()
        DB.create_all()
        self.today = datetime.utcnow().date()
        self.test_user = {'username': 'martin', 'email': 'martin@mail.com', 'password': 'password'}
        self.admin_user = dict(username='admin', email='admin@mail.com', password='admin1234', admin=True)
        self.meal_model = Meal
        self.order_model = Order
        self.menu_model = Menu
        self.order_model = Order
        self.user_model = User
        self.user1 = User(email='mike@mail.com', password='password', username='mail')
        self.user2 = User(email='bev@mail.com', username='bev',  password='password')

        self.menu = Menu()
        self.menu1 = Menu(date=datetime(year=2018, month=4, day=18))
        self.menu2 = Menu(date=datetime(year=2018, month=4, day=19))

        self.meal1 = Meal(name='Rice & Beef', price=100.00, description='Rice with beef. Yummy.')
        self.meal2 = Meal(name='Ugali Fish', price=150.00,
                          description='Ugali and fish, Nyanza tings!')
        self.meal3 = Meal(name='Muthokoi', price=100.00, description='Kamba tributes')

    def create_user(self):
        '''create test user'''
        user = self.user_model(username=self.test_user['username'], email=self.test_user['email'],
                               password=self.test_user['password'])
        user.save()
        return user
    
    def login_user(self):
        '''login test user'''
        self.create_user()
        username = self.test_user['username']
        password = self.test_user['password']
        user_info = dict(username=username, password=password)
        res = self.client.post(SIGNIN_URL, data=json.dumps(user_info))
        return res

    def login_admin(self):
        '''helper function to create an admin user and log them in '''
        res = self.client.post(SIGNUP_URL, data=json.dumps(self.admin_user))
        assert(res.status_code, 201)
        data = {'password': self.admin_user['password'], 'username': self.admin_user['username']}
        res = self.client.post(SIGNIN_URL, data=json.dumps(data))
        assert(res.status_code, 200)
        return res

    def create_meal(self):
        '''helper function to populate Meals so tests on menu and orders 
        can work'''
        meal = self.meal_model(name='Fish', price=100, description='Tasty Tilapia')
        meal.save()
        return meal

    def tearDown(self):
        # reset all database entries to empty dicts
        DB.session.remove()
        DB.drop_all()
        self.app_context.pop()
