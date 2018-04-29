'''Create a database'''
from datetime import datetime, timedelta
import jwt
from flask import current_app

TODAY = datetime.utcnow().date()


class ItemAlreadyExists(Exception):
    '''Exception when an object already exists'''
    pass


class UnknownClass(Exception):
    '''Exception for unknown or unexpectd datatypes'''
    pass


class BaseModel:
    '''Base model to be inherited  by other modells'''
    def make_dict(self):
        '''serialize class'''
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
    '''Class to represent the Meal objects'''
    def __init__(self, meal_id, name, price, description):
        self.meal_id = meal_id
        self.name = name
        self.price = price
        self.description = description

    def __str__(self):
        '''String representation of objects'''
        return '<Meal: {}'.format(self.name)


class User(BaseModel):
    """General user details"""

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.admin = False

    def __str__(self):
        '''String repr of the user objects'''
        return '<User: {}'.format(self.username)

    def validate_password(self, password):
        '''check if user password is correct'''
        return password == self.password

    def generate_token(self):
        '''generate access_token'''
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=120),
                'iat': datetime.utcnow(),
                'username': self.username,
            }
            token = jwt.encode(payload,
                               str(current_app.config.get('SECRET')),
                               algorithm='HS256'
                              )
            return token
        except Exception as err:
            return str(err)

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
    '''Class for admin/caterer objects'''
    def __init__(self, username, email, password, admin=True):
        User.__init__(self, username=username, email=email, password=password)
        self.admin = admin


class Order(BaseModel):
    '''class for orders'''
    def __init__(self, order_id, username, meal, quantity=1,):
        self.meal_id = meal
        self.quantity = quantity
        self.order_id = order_id
        self.order_by = username


class Menu(BaseModel):
    '''model for Menus'''
    def __init__(self, meals, date=TODAY):
        self.meals = meals
        self.date = str(date)


class Database:
    '''Database to store records'''
    def __init__(self):
        self.admins = {}
        self.meals = {}
        self.users = {}
        self.users_email = {}
        self.current_menu = {}
        self.orders = {}
        self.user_orders = {}

    def add(self, item):
        '''add object to respective holder'''
        if isinstance(item, User):
            if item.username in self.users.keys() or item.email in self.users_email.keys():
                raise ItemAlreadyExists('User exists')
            else:
                self.users.update({str(item.username): item})
                self.users_email.update({str(item.email): item})
        elif isinstance(item, Admin):
            if item.username in self.users.keys():
                raise ItemAlreadyExists('Admin exists')
            else:
                self.admins.update({str(item.username): item})
                self.users.update({str(item.username): item})
                self.users_email.update({str(item.email): item})

        elif isinstance(item, Meal):
            if str(item.meal_id) in self.meals.keys():
                raise ItemAlreadyExists('Meal exists')
            else:
                self.meals.update({str(item.meal_id): item})

        elif isinstance(item, Menu):
            if str(item.date) in self.current_menu.keys():
                raise ItemAlreadyExists('Menu exists')
            else:
                self.current_menu.update({str(item.date): item})

        elif isinstance(item, Order):
            if str(item.order_id) in self.orders.keys():
                raise ItemAlreadyExists('Order exists')
            else:
                self.orders.update({str(item.order_id): item})
            if str(item.order_by) in self.user_orders.keys():
                self.user_orders[str(item.order_by)].append(item)
            else:
                self.user_orders.update({str(item.order_by): [item]})
        else:
            return 'Unknown type'

    def get_user_by_username(self, username):
        '''search users by username'''
        return self.users.get(username, '')

    def get_user_by_email(self, email):
        '''search users by email'''
        return self.users_email.get(email, '')


if __name__ == '__main__':
    DATABASE = Database()
