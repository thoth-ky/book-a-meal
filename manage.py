'''module for app management'''

import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
# local imports
try:
    from app import create_app, DB
    from app.models.models import User
except ModuleNotFoundError:
    from .app import create_app, DB
    from .app.models.models import User

# initialize app with all its configs
APP = create_app(config_name=os.getenv('APP_SETTINGS'))
MIGRATE = Migrate(APP, DB)
MANAGER = Manager(APP)

# Define the migration command to always be preceded by the word "db"
# Example usage: python manage.py db init
MANAGER.add_command('db', MigrateCommand)


@MANAGER.command
def create_super_user():
    username = input('Enter superuser username: ')
    email  = input('Enter super user email: ')
    password = input('Enter superuser pasword: ')
    user = User(username=username, email=email, password=password)
    user.admin = True
    user.super_user = True
    err =   user.save()
    if err:
        print(err)
    print('Super User created successfully')


if __name__ == "__main__":
    MANAGER.run()
