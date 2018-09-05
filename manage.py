'''module for app management'''

import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
# local imports
try:
    from app import create_app, DB
    from app.models import User, Meal
except ModuleNotFoundError:
    from .app import create_app, DB
    from .app.models import User, Meal

# initialize app with all its configs
APP = create_app(config_name=os.getenv('APP_SETTINGS'))
MIGRATE = Migrate(APP, DB)
MANAGER = Manager(APP)

# Define the migration command to always be preceded by the word "db"
# Example usage: python manage.py db init
MANAGER.add_command('db', MigrateCommand)


@MANAGER.command
def create_super_user():
    '''fuction to create super user directly'''
    username = input('Enter superuser username: ')
    email  = input('Enter super user email: ')
    password = input('Enter superuser pasword: ')
    user = User(username=username, email=email, password=password)
    user.admin = True
    user.super_user = True
    err =   user.save()
    if err:
        print(err)
    else:
        print('Super User created successfully')

@MANAGER.command
def make_admin():
    '''function to make users admin'''
    username = input('Enter username to promote to admin: ')
    user = User.get(username=username)
    if user:
        user.admin = True
        err =   user.save()
        if err:
            print(err)
        else:
            print('User {} successfully promoted to admin'.format(username))
    else:
        print("That user does not exist")

@MANAGER.command
def create_default_meals():
    '''function to make users admin'''
    name = input('Enter name of the meal: ')
    while True:
        price = input('Enter price: ')
        try:
            price = int(price)
            break
        except:
            print('Price should be integer')
            continue
    
    description = input('Add a short description of the meal: ')
    while True:
        username = input('Enter name of caterer in charge of this meal: ')
        user = User.get(username=username)
        if isinstance(user, User):
            break
        else:
            print('User not available, please provide a valid username.')
            continue


    meal = Meal(name=name, price=price, description=description, default=True)
    meal.user_id = user.user_id
    meal.save()
    print('Meal successfully created as default.')



if __name__ == "__main__":
    MANAGER.run()
