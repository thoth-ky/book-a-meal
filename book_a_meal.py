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
config = os.environ.get('APP_SETTINGS') or 'development'

app = create_app(config)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run('', port=port)
