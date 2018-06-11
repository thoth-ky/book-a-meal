'''Declares all stuff shared by models here'''
import time
import random
from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from sqlalchemy.orm import relationship, backref
from sqlalchemy import (Table, Column, Integer, ForeignKey, String, Boolean,
                        Float, DateTime)
# local imports
from .. import DB, AUTH


MENU_MEALS = DB.Table(
    'menu_meals',
    DB.Column('menu_id', DB.Integer(), DB.ForeignKey('menu.id')),
    DB.Column('meal_id', DB.Integer(), DB.ForeignKey('meal.meal_id')))


class MealAssoc(DB.Model):
    __tablename__ = 'meals_assoc'
    meal_id = Column(Integer, ForeignKey('meal.meal_id'), primary_key=True)
    order_id = Column(Integer, ForeignKey('order.order_id'),
                      primary_key=True)
    quantity = Column(Integer)


class BaseModel(DB.Model):
    '''Base model to be inherited  by other modells'''
    __abstract__ = True

    def make_dict(self):
        '''serialize class'''
        return {col.name: getattr(self, col.name)
                for col in self.__table__.columns}

    def save(self):
        '''save object'''
        try:
            DB.session.add(self)
            DB.session.commit()
            return None
        except Exception as e:
            DB.session.rollback()
            return {
                'message': 'Save operation not successful',
                'error': str(e)
            }

    def delete(self):
        '''delete object'''
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
        '''new_data is a dictionary containing the field as key and new value
        as value'''
        for key in new_data.keys():
            self.put(key, new_data[key])

    def put(self, field, value):
        '''insert operation. field is the attribute name and value is the
        value being inseted, it can be a list or not. A list is used to
        populate a relationship field'''
        if isinstance(value, list):
            old_value = getattr(self, field)
            old_value.extend(value)
            self.save()
        else:
            setattr(self, field, value)
            self.save()

    @classmethod
    def has(cls,**kwargs):
        '''check if table contains record atching given kwargs'''
        obj = cls.query.filter_by(**kwargs).first()
        if isinstance(obj, cls):
            return True
        return False

    @classmethod
    def get(cls, **kwargs):
        '''get a record from table matching given kwarg'''
        return cls.query.filter_by(**kwargs).first()

    @classmethod
    def get_all(cls):
        '''return a list of all records in the table'''
        return cls.query.all()


class User(BaseModel):
    """General user details"""
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    admin = Column(Boolean, default=False)
    super_user = Column(Boolean, default=False)
    orders = relationship('Order', backref='owner', lazy=True, uselist=True)
    meals = relationship('Meal', backref='caterer', lazy=True, uselist=True)

    def __init__(self, username, email, password):
        '''necessary to avoid setting admins directly'''
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.admin = False

    @AUTH.verify_password
    def validate_password(self, password):
        '''check if user password is correct'''
        return check_password_hash(self.password_hash, password)

    def view(self):
        '''display user informtion, hide sensitive values'''
        user = self.make_dict()
        user['password_hash'] = '*'*10
        return user
        
    def generate_token(self):
        '''generate access_token, validity is period of time before it
        becomes invalid'''
        validity = current_app.config.get('TOKEN_VALIDITY')
        payload = {
            'exp': datetime.utcnow() + timedelta(minutes=validity),
            'iat': datetime.utcnow(),
            'username': self.username,
            'admin': self.admin,
            'superuser': self.super_user
        }
        token = jwt.encode(payload,
                            str(current_app.config.get('SECRET')),
                            algorithm='HS256'
                            )
        return token

    @staticmethod
    def decode_token(token):
        '''decode access token from authorization header'''
        try:
            payload = jwt.decode(
                token, str(current_app.config.get('SECRET')),
                algorithms=['HS256'])
            return payload
        except Exception:
            # the token is invalid, return an error string
            raise jwt.InvalidTokenError(
                "Invalid token. Please register or login")

    @staticmethod
    def promote_user(user):
        '''make user admin'''
        user.admin = True
        user.save()


class Meal(BaseModel):
    '''Class to represent the Meal objects'''

    __tablename__ = 'meal'

    meal_id = Column(Integer(), primary_key=True)
    name = Column(String(40), nullable=False)
    price = Column(Float(), nullable=False, )  # specify d.p
    description = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    orders = relationship('MealAssoc', backref='meal', lazy=True, uselist=True)

    def view(self):
        '''display meal'''
        return {
            'meal_id': self.meal_id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'caterer': self.caterer.username
        }

    def order_view(self):
        '''display meal orders'''
        return [
            {"order_id": a.order_id,
             "time_ordered": a.orders.time_ordered,
             "due_time": a.orders.due_time.ctime(),
             "quantity": a.quantity,
             "order_by": a.orders.owner.username
            } for a in self.orders]


class Menu(BaseModel):
    '''model for Menus'''

    __tablename__ = 'menu'

    id = Column(
        Integer,
        primary_key=True
        )
    date = Column(
        DateTime, 
        default=datetime.utcnow().date(),
        unique=True)
    meals = relationship(
        'Meal',
        secondary='menu_meals',
        backref=backref('menu_meals', lazy=True, uselist=True))
    
    def __init__(self, date=None):
        if date:
            self.date = date
        else:
            today = datetime.utcnow().date()
            self.date = datetime(
                year=today.year, month=today.month, day=today.day)

    def add_meal(self, meal, date=None):
        '''Add meal to menu'''
        if not date:
            today = datetime.utcnow().date()
            date = datetime(year=today.year, month=today.month, day=today.day)
        
        menu = Menu.query.filter_by(date=date).first()
        if not menu:
            menu = Menu(date=date)
        if isinstance(meal, Meal):
            meal = [meal]
        self.put('meals', meal)
        self.save()
    
    def view(self):
        '''display menu'''
        meals = []
        if self.meals:
            meals = [{'meal_id':meal.meal_id,
                      'name': meal.name,
                      'price': meal.price,
                      'description': meal.description } for meal in self.meals]
        return {
            'id': self.id,
            'date': self.date.ctime(),
            'meals': meals
        }


class Order(BaseModel):
    '''class for orders'''

    __tablename__ = 'order'

    order_id = Column(Integer, primary_key=True)
    time_ordered = Column(Float, default=time.time())
    due_time = Column(
        DateTime, default=datetime.utcnow()+timedelta(minutes=30))
    user_id = Column(
        Integer, ForeignKey('user.user_id'))
    meal = relationship(
        'MealAssoc', backref='orders', lazy='dynamic', uselist=True)

    def view(self):
        '''display order details'''
        assoc_data = self.meal.all()
        order_meals = [{'meal_id': a.meal.meal_id,
                        'name': a.meal.name,
                        'quantity': a.quantity,
                        'unit_price': a.meal.price,
                        'caterer': a.meal.caterer.username
                       } for a in assoc_data]
        return {
            'order_id': self.order_id,
            'time_ordered': self.time_ordered,
            'due_time': self.due_time.ctime(),
            'owner': self.owner.username,
            'meals': order_meals
        }
    
    def update_order(self, meal_id, quantity):
        '''Update order details'''
        assoc_data = self.meal.filter_by(meal_id=meal_id).first()
        assoc_data.quantity = quantity
        self.save()
        
    def __init__(self, user_id, time_ordered=None, due_time=None):
        self.user_id = user_id
        if time_ordered:
            self.time_ordered = time_ordered
        if due_time:
            self.due_time = due_time

    def add_meal_to_order(self, meal, quantity=1):
        '''add a meal to order'''
        assoc = MealAssoc(quantity=quantity)
        assoc.meal = meal
        self.meal.append(assoc)

    def editable(self, now=None):
        '''checks if it's allowed to edit order'''
        time_limit = int(current_app.config.get('ORDER_EDITS_UPTO'))
        if now is None:
            now = int(time.time())
        time_lapsed = now - self.time_ordered
        if time_lapsed >= time_limit:
            return False
        return True
