'''
This script creates a flask app and runs it at specified host and port,
'''
import os
# local imports
from app import create_app

# get configuration environment
config = os.environ.get('APP_SETTINGS')

app = create_app(config)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)