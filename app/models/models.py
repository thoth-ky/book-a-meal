'''Declares all stuff shared by models here'''
import time
from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from sqlalchemy.orm import relationship, backref


# local imports
from .. import DB

ORDER_MEALS = DB.Table(
    'order_dishes',
    DB.Column('order_id',DB.Integer(), DB.ForeignKey('order.id')),
    DB.Column('meal_meal_id', DB.Integer(), DB.ForeignKey('meal.meal_id')))

MENU_MEALS = DB.Table(
    'menu_meals',
    DB.Column(
        'menu_id',
        DB.Integer(),
        DB.ForeignKey('menu.id')),
    DB.Column(
        'meal_meal_id',
        DB.Integer(),
        DB.ForeignKey('meal.meal_id')))


class BaseModel(DB.Model):
    '''Base model to be inherited  by other modells'''
    __abstract__ = True

    def make_dict(self):
        '''serialize class'''
        # dictionary = {col.name: getattr(self, col.name) for col in self.__table__.DB.Columns}
        return self.__dictt__

    def save(self):
        '''save object'''
        try:
            DB.session.add(self)
            DB.session.commit()
        except Exception as e:
            DB.session.roollback()
            return {
                'message': 'Save operation not successful',
                'error': str(e)
            }

    def delete(self):
        '''delete'''
        try:
            DB.session.delete(self)
            DB.session.commit()
        except Exception as e:
            DB.session.rollback()
            return {
                'message': 'Delete operation failed',
                'error': str(e)
            }

    def update(self, new_data):
        '''new_data is a dictionary containing new info'''
        current_data = self.make_dict()
        data_keys = current_data.keys()
        new_keys = new_data.keys()
        for key in data_keys:
            for new_data_key in new_keys:
                if key == new_data_key:
                    current_data[key] = new_data[new_data_key]

    def put(self):
        raise AttributeError('Not Implemented')        


class User(BaseModel):
    """General user details"""
    user_id = DB.Column(DB.Integer, primary_key=True)
    email = DB.Column(DB.String, unique=True, nullable=False)
    username = DB.Column(DB.String, unique=True, nullable=False)
    password_hash = DB.Column(DB.String, nullable=False)
    caterer = DB.Column(DB.Boolean, default=False)
    orders = relationship('Order', back_populates='parent')


    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.admin = False

    def __repr__(self):
        '''DB.String repr of the user objects'''
        return '<User: {}'.format(self.username)

    def validate_password(self, password):
        '''check if user password is correct'''
        return check_password_hash(self.password_hash, password)

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


class Meal(BaseModel):
    '''Class to represent the Meal objects'''
    meal_id = DB.Column(DB.Integer(), primary_key=True)
    name = DB.Column(DB.String(40), unique=True)
    price = DB.Column(DB.Float(), nullable=False, )  # specify d.p
    description = DB.Column(DB.String(250), nullable=False)
    available = DB.Column(DB.Boolean(), default=False)
    
    def __init__(self, meal_id, name, price, description):
        self.meal_id = meal_id
        self.name = name
        self.price = price
        self.description = description

    def now_available(self):
        '''method to set meal to available'''
        self.available = True

    def add_to_menu(self):
        '''method to add meal to todays menu'''
        Menu.add_meal(self)

    def place_order(self, cart_id, quantity=1):
        '''Add meal to order'''
        Order.add_meal(self, quantity)

    def __repr__(self):
        '''String representation of objects'''
        return '<Meal: {}'.format(self.name)


class Menu(BaseModel):
    '''model for Menus'''
    id = DB.Column(DB.Integer, primary_key=True)
    date = DB.Column(DB.DateTime, default=datetime.utcnow().date(), unique=True)
    meals = relationship(
        'Meal', secondary='menu_meals', backref=backref('meals', lazy=True, uselist=True))

    def __repr__(self):
        '''class instance rep'''
        return '<Menu Date {}>'.format(self.date.ctime())
    
    @staticmethod
    def add_meal(meal):
        '''Add meal to menu'''
        today = datetime.utcnow().date()
        menu = Menu.query.filter_by(date=today).first()
        if not menu:
            menu = Menu()
        menu.meals.put(meal)


class Order(BaseModel):
    '''class for orders'''
    id = DB.Column(DB.Integer, primary_key=True)
    time_ordered = DB.Column(DB.DateTime, default=time.time())
    quantity = DB.Column(DB.Integer, default=1)
    meal = relationship('Meal', secondary='order_dishes', backref=backref('meals', lazy=True, uselist=True))
    user_id = DB.Column(DB.Integer, DB.ForeignKey('user.user_id'))
    user = relationship('User', back_populates='orders')

    def __init__(self, meal, quantity=1, time=time.time()):
        self.quantity = quantity
        self.time_ordered = time

    @staticmethod
    def add_meal(meal, quantity):
        '''add a meal to order'''
        order = Order()
        order.put(meal, quantity)

    def __repr__(self):
        return '<Order {}>'.format(self.order_id)
