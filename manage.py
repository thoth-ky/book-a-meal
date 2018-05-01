'''module for app management'''

import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
# local imports
try:
    from app import create_app, DB
except ModuleNotFoundError:
    from .app import create_app, DB

# initialize app with all its configs
APP = create_app(config_name=os.getenv('APP_SETTINGS'))
MIGRATE = Migrate(APP, DB)
MANAGER = Manager(APP)

# Define the migration command to always be preceded by the word "db"
# Example usage: python manage.py db init
MANAGER.add_command('db', MigrateCommand)


if __name__ == "__main__":
    MANAGER.run()
