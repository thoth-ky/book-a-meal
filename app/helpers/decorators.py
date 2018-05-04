from functools import wraps
from flask import request
# local imports
from ..models.models import User

def token_required(f):
    '''checks user have valid tokens'''
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization', None)
            access_token = auth_header.split(' ')[1]
            if access_token:
                username = User.decode_token(access_token)
                user = User.get(username=username)
                return f(user=user, *args, **kwargs)
            return {'message':"Please login first, your session might have expired"}, 401
        except Exception as e:
            return {'message': 'An error occured', 'error':str(e)},400
    return decorated


def admin_token_required(f):
    '''check users have valid tokens and they have admin property'''
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization', None)
            access_token = auth_header.split(' ')[1]
            if access_token:
                username = User.decode_token(access_token)

                user = User.get(username=username)
                if user.admin == True:
                    return f(user=user, *args, **kwargs)
                return {'message': 'Unauthorized'}, 401
            return {'message':"Please login first, your session might have expired"}, 401
        except Exception as e:
            return {'message': 'An error occured', 'error':str(e)},400
    return decorated