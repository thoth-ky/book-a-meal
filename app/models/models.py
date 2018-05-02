'''Declares all stuff shared by models here'''
import time
import random
from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from sqlalchemy.orm import relationship, backref


# local imports
from .. import DB

# ORDER_MEALS = DB.Table(
#     'order_meals',
#     DB.Column('order_id', DB.Integer(), DB.ForeignKey('order.id')),
#     DB.Column('meal_id', DB.Integer(), DB.ForeignKey('meal.meal_id')))

MENU_MEALS = DB.Table(
    'menu_meals',
    DB.Column('menu_id', DB.Integer(), DB.ForeignKey('menu.id')),
    DB.Column('meal_id', DB.Integer(), DB.ForeignKey('meal.meal_id')))


class BaseModel(DB.Model):
    '''Base model to be inherited  by other modells'''
    __abstract__ = True

    def make_dict(self):
        '''serialize class'''
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}
        # return  self.__dict__

    def save(self):
        '''save object'''
        try:
            DB.session.add(self)
            DB.session.commit()
            return None
        except Exception as e:
            raise e
            DB.session.rollback()
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
        '''new_data is a dictionary containing the field as key and new value as value'''
        for key in new_data.keys():
            try:
                self.__dict__[key] = new_data[key]
            except KeyError:
                return 'Invalid field name: {}'.format(key)

    def put(self, field, value):
        if isinstance(value, list):
            old_value = getattr(self, field)
            old_value.extend(value)
            self.save()
        else:
            setattr(self, field, value)
            self.save()

    @classmethod
    def has(cls,**kwargs):
        obj = cls.query.filter_by(**kwargs).first()
        if obj:
            return True
        return False

    @classmethod
    def get(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()


class User(BaseModel):
    """General user details"""
    __tablename__ = 'user'
    user_id = DB.Column(DB.Integer, primary_key=True)
    email = DB.Column(DB.String, unique=True, nullable=False)
    username = DB.Column(DB.String, unique=True, nullable=False)
    password_hash = DB.Column(DB.String, nullable=False)
    admin = DB.Column(DB.Boolean, default=False)
    super_user = DB.Column(DB.Boolean, default=False)
    orders = relationship('Order', backref='owner', lazy='dynamic')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.admin = False

    def __repr__(self):
        '''DB.String repr of the user objects'''
        return '<User: {}>'.format(self.username)

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

    @staticmethod
    def promote_user(user):
        user.admin = True
        user.save()


class Meal(BaseModel):
    '''Class to represent the Meal objects'''
    __tablename__ = 'meal'

    meal_id = DB.Column(DB.Integer(), primary_key=True)
    name = DB.Column(DB.String(40), unique=True)
    price = DB.Column(DB.Float(), nullable=False, )  # specify d.p
    description = DB.Column(DB.String(250), nullable=False)
    available = DB.Column(DB.Boolean(), default=False)
    orders = relationship('Order', backref='meal', lazy='dynamic')
    
    def __init__(self, name, price, description):
        self.name = name
        self.price = price
        self.description = description

    def now_available(self):
        '''method to set meal to available'''
        self.available = True

    def add_to_menu(self):
        '''method to add meal to todays menu'''
        Menu.add_meal(self)

    def place_order(self, order_id, user_id, quantity=1):
        '''Add meal to order'''
        Order(meal_id=self.meal_id, order_id=order_id, quantity=quantity, user_id=user_id)

    def __repr__(self):
        '''String representation of objects'''
        return '<Meal: {}'.format(self.name)


class Menu(BaseModel):
    '''model for Menus'''
    __tablename__ = 'menu'

    id = DB.Column(DB.Integer, primary_key=True)
    date = DB.Column(DB.DateTime, default=datetime.utcnow().date(), unique=True)
    meals = relationship(
        'Meal', secondary='menu_meals', backref=backref('menu_meals', lazy=True, uselist=True))

    def __repr__(self):
        '''class instance rep'''
        return '<Menu Date {}>'.format(self.date.ctime())
    
    def add_meal(self, meal):
        '''Add meal to menu'''
        today = datetime.utcnow().date()
        menu = Menu.query.filter_by(date=today).first()
        if not menu:
            menu = Menu()
        if isinstance(meal, Meal):
            meal = [meal]
        self.put('meals', meal)


class Order(BaseModel):
    '''class for orders'''
    __tablename__ = 'order'
    id = DB.Column(DB.Integer, primary_key=True)
    order_id = DB.Column(DB.String(50), nullable=False)
    time_ordered = DB.Column(DB.Float, default=time.time())
    quantity = DB.Column(DB.Integer, default=1)
    user_id = DB.Column(DB.Integer, DB.ForeignKey('user.user_id'))
    meal_id = DB.Column(DB.Integer, DB.ForeignKey('meal.meal_id'))
    # meal = relationship(
    #     'Meal', secondary='order_meals', backref=backref('meal_orders', lazy=True, uselist=True))

    def __init__(self, order_id, meal, user_id, quantity=1):
        self.order_id = order_id
        self.user_id = user_id
        self.quantity = quantity
        # self.meal = [meal]
        self.meal_id = meal.meal_id

    def __repr__(self):
        return '<Order {}>'.format(self.order_id)

    def editable(self):
        '''checks if it's allowed to edit order'''
        time_limit = int(current_app.config.get('ORDER_EDITS_UPTO'))
        now = time.time()
        if self.time_ordered - now >= time_limit:
            return False
        return True

    @staticmethod
    def generate_order_id():
        order_id =''
        chars = 'ABCDEFGHIJKLMNOPQRQSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()'
        order_id_length = 50
        for y in range(order_id_length):
            order_id += chars[random.randint(0, len(chars) - 1)]
        return order_id
