'''
This script creates a flask app and runs it at specified host and port,
'''
import os
# local imports
try:
    from app import create_app, DB
except ModuleNotFoundError:
    from .app import create_app, DB

# get configuration environment
CONFIG = os.environ.get('APP_SETTINGS') or 'development'

APP = create_app(CONFIG)

@APP.shell_context_processor
def  make_shell_context():
    '''
    context when flask shell runs to avoid cumbersome imports'''
    return {
        'db': DB
    }


if __name__ == '__main__':
    # PORT = int(os.environ.get('PORT', 5000))
    # APP.run('', port=PORT, debug=True)
    APP.run()
