'''
This script creates a flask app and runs it at specified host and port,
'''
import os
# local imports
try:
    from app import create_app
except ModuleNotFoundError:
    from .app import create_app

# get configuration environment
CONFIG = os.environ.get('APP_SETTINGS') or 'development'

APP = create_app(CONFIG)


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    APP.run('', port=PORT)
