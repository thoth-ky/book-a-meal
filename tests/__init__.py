'''This contains a a basetest case'''
from datetime import datetime
from unittest import TestCase
import json
# local imports
from app import create_app, DB
from app.models.models import Meal, Order, Menu
from app.models.authmodels import User

SIGNUP_URL = '/api/v2/auth/signup'
SIGNIN_URL = '/api/v2/auth/signin'


class BaseTestClass(TestCase):
    '''An abstract base class for tests, contains all common variables
    methods'''
    def setUp(self):
        '''Declare initial variables'''
        self.maxDiff = None
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.database = DB
        DB.drop_all()
        DB.create_all()
        self.today = datetime.utcnow().date()
        self.test_user = {
            'username': 'martin',
            'email': 'martin@mail.com',
            'password': 'password'}
        self.admin_user = dict(
            username='admin',
            email='admin@mail.com',
            password='admin1234',
            admin=True)
        self.meal_model = Meal
        self.order_model = Order
        self.menu_model = Menu
        self.order_model = Order
        self.user_model = User
        self.user1 = User(email='mike@mail.com', password='password',
                          username='mike')
        self.user2 = User(email='bev@mail.com', username='bevah',
                          password='password')

        self.menu = Menu()
        self.menu1 = Menu(date=datetime(year=2019, month=4, day=18))
        self.menu2 = Menu(date=datetime(year=2019, month=4, day=19))

        self.meal1 = Meal(name='Rice & Beef', price=100.00,
                          description='Rice with beef. Yummy.')
        self.meal2 = Meal(name='Ugali Fish', price=150.00,
                          description='Ugali and fish, Nyanza tings!')
        self.meal3 = Meal(name='Muthokoi', price=100.00,
                          description='Kamba tributes')
        
    def create_user(self):
        '''create test user'''
        user = self.user_model(
            username=self.test_user['username'],
            email=self.test_user['email'],
            password=self.test_user['password'])
        user.save()
        return user
    
    def login_user(self):
        '''login test user'''
        user = self.create_user()
        return user.generate_token().decode()

    def login_admin(self):
        '''helper function to create an admin user and log them in '''
        admin = self.user_model(password=self.admin_user['password'],
                                username=self.admin_user['username'],
                                email=self.admin_user['email'])
        admin.admin = True
        admin.save()
        return admin.generate_token().decode()

    def login_super_admin(self):
        '''helper function to create and login super admin'''
        super_admin = self.user_model(username='super', email='super@bam.com',
                                      password='super1234')
        super_admin.admin = True
        super_admin.super_user = True
        super_admin.save()
        return super_admin.generate_token().decode()

    def create_meal(self, username=None):
        '''helper function to populate Meals so tests on menu and orders 
        can work'''
        meal = self.meal_model(name='Fish', price=100, description='Tasty Tilapia')
        if username:
            user_id = self.user_model.get(username=username).user_id
            meal.user_id = user_id
        meal.save()
        return meal

    def tearDown(self):
        # reset all database entries to empty dicts
        DB.session.remove()
        DB.drop_all()
        self.app_context.pop()
