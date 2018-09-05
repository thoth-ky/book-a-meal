'''Declares all stuff shared by models here'''
import time
import random
from datetime import datetime, timedelta
# local imports
from .. import DB
from flask import current_app
from .base import BaseModel
from sqlalchemy import (Table, Column, Integer, ForeignKey, String, Boolean,
                        Float, DateTime)
from sqlalchemy.orm import relationship, backref


MENU_MEALS = DB.Table(
    'menu_meals',
    DB.Column('menu_id', DB.Integer(), DB.ForeignKey('menu.id')),
    DB.Column('meal_id', DB.Integer(), DB.ForeignKey('meal.meal_id', ondelete='CASCADE')))


class MealAssoc(BaseModel):
    __tablename__ = 'meals_assoc'
    meal_id = Column(Integer, ForeignKey('meal.meal_id'), primary_key=True)
    order_id = Column(Integer, ForeignKey('order.order_id'),
                      primary_key=True)
    quantity = Column(Integer)


class Meal(BaseModel):
    '''Class to represent the Meal objects'''

    __tablename__ = 'meal'

    meal_id = Column(Integer(), primary_key=True)
    name = Column(String(40), nullable=False)
    price = Column(Float(), nullable=False, )  # specify d.p
    description = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    orders = relationship('MealAssoc', backref='meal', lazy=True, uselist=True)
    default = Column(Boolean, default=False)

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
             "time_ordered": int(a.orders.time_ordered),
             "due_time": a.orders.due_time.isoformat(),
             "quantity": a.quantity,
             "order_by": a.orders.owner.username,
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
                      'description': meal.description,
                      'caterer': meal.caterer.username } for meal in self.meals]
        return {
            'id': self.id,
            'date': self.date.timestamp(),
            'meals': meals
        }

    @staticmethod
    def get_by_date(date):
        menu = Menu.get(date=date)
        if menu:
            menu = menu.view()
        else:
            menu = {
                'date': date.timestamp(),
                'meals': []
            }
        default_meals = Meal.query.filter_by(default=True).all()
        default_meals = [meal.view() for meal in default_meals]
        menu['meals'].extend(default_meals)
        if menu['meals']:
            return menu
        return None

class Order(BaseModel):
    '''class for orders'''

    __tablename__ = 'order'

    order_id = Column(Integer, primary_key=True)
    time_ordered = Column(Float, default=time.time())
    due_time = Column(
        DateTime, default=datetime.utcnow()+timedelta(minutes=30))
    is_served = Column(Boolean, default=False)
    user_id = Column(
        Integer, ForeignKey('user.user_id'))
    meal = relationship(
        'MealAssoc', backref='orders', lazy='dynamic', uselist=True)


    def __init__(self, user_id, time_ordered=None, due_time=None):
        self.user_id = user_id
        if time_ordered:
            self.time_ordered = time_ordered
        if due_time:
            self.due_time = due_time

    def view(self):
        '''display order details'''
        assoc_data = self.meal.all()
        order_meals = [{'meal_id': a.meal.meal_id,
                        'name': a.meal.name,
                        'quantity': a.quantity,
                        'unit_price': a.meal.price,
                        'caterer': a.meal.caterer.username,
                        'sub_total': a.quantity * a.meal.price
                       } for a in assoc_data]
        return {
            'order_id': self.order_id,
            'time_ordered': int(self.time_ordered),
            'due_time': self.due_time.timestamp(),
            'owner': self.owner.username,
            'meals': order_meals,
            'total': sum([meal['sub_total'] for meal in order_meals])
        }

    def update_order(self, meal_id, quantity):
        '''Update order details'''
        assoc_data = self.meal.filter_by(meal_id=meal_id).first()
        assoc_data.quantity = quantity
        self.save()

    def remove_meal(self, meal_id):
        '''remove meal from the order'''
        assoc_data = self.meal.all()
        for dish in assoc_data:
            if dish.meal.meal_id == meal_id:
                dish.delete()

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
        if time_lapsed >= time_limit or self.is_served == True:
            return False
        return True
