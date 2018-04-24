'''Create a database'''
from datetime import datetime


today = datetime.utcnow().date()


class BaseModel:
    
    @classmethod
    def make_dict(cls):
        return cls.__dict__


class Meal(BaseModel):
    def __init__(self, meal_id, name, price, description):
        self.meal_id = meal_id
        self.name = name
        self.price = price
        self.description = description


class User(BaseModel):
    """docstring for User"""
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


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