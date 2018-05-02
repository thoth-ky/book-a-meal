'''Create a database'''
from .user import User
from .menu import Menu
from .admin import Admin
from .meal import Meal
from .order import Order
from . import ItemAlreadyExists


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
