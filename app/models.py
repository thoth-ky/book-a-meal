'''Create a database'''
from datetime import datetime, timedelta
import jwt
from flask import current_app

today = datetime.utcnow().date()


class BaseModel:
    
    def make_dict(self):
        return self.__dict__

    def update(self, new_data):
        '''new_data is a dictionary containing new info'''
        current_data = self.make_dict()
        data_keys = current_data.keys()
        new_keys = new_data.keys()
        for key in data_keys:
            for new_data_key in new_keys:
                if key == new_data_key:
                    current_data[key] = new_data[new_data_key]


class Meal(BaseModel):
    def __init__(self, meal_id, name, price, description):
        self.meal_id = meal_id
        self.name = name
        self.price = price
        self.description = description


class User(BaseModel):
    """General user details"""
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def validate_password(self, password):
        '''check if user password is correct'''
        if password == self.password:
            return True
        else:
            return False

    @staticmethod
    def generate_token(self, username):
        '''generate access_token'''
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=120),
                'iat': datetime.utcnow(),
                'username': username,
            }
            token = jwt.encode(
                payload,
                str(current_app.config.get('SECRET')),
                algorithm='HS256'
                )
        except Exception as e:
            return str(e)

    @staticmethod
    def decode_token(token):
        '''decode access token from authorization header'''
        try:
            payload = jwt.decode(token, str(current_app.config.get('SECRET')))
            return payload['username']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return "Invalid token. Please register or login"


class Admin(User):
    def __init__(self, username, email, password, admin=True):
        User.__init__(username, email, password)
        self.admin = admin


class Order(BaseModel):
    def __init__(self, meals=[], quantity=1):
        self.meals = meals
        self.quantity = quantity


class Menu(BaseModel):
    def __init__(self, meals=[], date=today):
        self.meals = meals
        date = date
        

class Database:
    def __init__(self):
        self.admins = []
        self.meals = []
        self.users = []
        self.current_menu = []
        self.orders = []

    def add(self, item):
        if isinstance(item, User):
            # add to users
            self.users.append(item)
        elif isinstance(item, Meal):
            # add to meals
            self.meals.append(item)
        elif isinstance(item, Menu):
            # add to current menu
            self.current_menu.append(item)
        elif isinstance(item, Order):
            # add to orders
            self.orders.append(item)
        elif isinstance(item, Admin):
            # add to admins
            self.admins.append(item)
        else:
            return 'Unknown type'