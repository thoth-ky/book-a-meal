'''Create a database'''
from datetime import datetime, timedelta
import jwt
from flask import current_app

today = datetime.utcnow().date()


class ItemAlreadyExists(Exception):
    pass


class BadToken(Exception):
    pass


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
        self.admin = False

    def validate_password(self, password):
        '''check if user password is correct'''
        if password == self.password:
            return True
        else:
            return False

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
            return token
        except Exception as e:
            return str(e)

    @staticmethod
    def decode_token(token):
        '''decode access token from authorization header'''
        try:
            payload = jwt.decode(
                token, str(current_app.config.get('SECRET')), algorithms=['HS256'])
            return payload['username']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return "Invalid token. Please register or login"


class Admin(User):
    def __init__(self, username, email, password, admin=True):
        User.__init__(self, username=username, email=email, password=password)
        self.admin = admin


class Order(BaseModel):
    def __init__(self, order_id, username, meal, quantity=1,):
        self.meal_id = meal
        self.quantity = quantity
        self.order_id = order_id
        self.order_by = username


class Menu(BaseModel):
    def __init__(self, meals=[], date=today):
        self.meals = meals
        self.date = str(date)
        

class Database:
    def __init__(self):
        self.admins = {}
        self.meals = {}
        self.users = {}
        self.users_email = {}
        self.current_menu = {}
        self.orders = {}
        self.user_orders = {}

    def add(self, item):
        if isinstance(item, User):
            if (item.username in self.users.keys() or item.email in self.users_email.keys()):
                raise ItemAlreadyExists('User exists')
            else:
                self.users.update({str(item.username): item})
                self.users_email.update({str(item.email): item})
        elif isinstance(item, Admin):
            self.admins.update({str(item.username): item})
        elif isinstance(item, Meal):
            self.meals.update({str(item.meal_id): item})
        elif isinstance(item, Menu):
            self.current_menu.update({str(item.date): item})
        elif isinstance(item, Order):
            self.orders.update({str(item.order_id): item})
            self.users.update({str(item.order_by): item})
        else:
            return 'Unknown type'

    def get_user_by_username(self, username):
        return self.users.get(username, '')

    def get_user_by_email(self, email):
        return self.users_email.get(email, '')

    
if __name__ == '__main__':
    database = Database()