import jwt
from functools import wraps
from flask import request
from ..models.models import User, Meal

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            access_token = auth_header.split(' ')[1]
            if access_token:
                username = User.decode_token(access_token)
                user = User.get(username=username)
                return f(user, *args, **kwargs)
            return {'message':"Please login first, your session might have expired"}, 401
        except Exception as e:
            return {'message': 'An error occured', 'error':str(e)},400
    return decorated


def admin_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            access_token = auth_header.split(' ')[1]
            if access_token:
                username = User.decode_token(access_token)
                user = User.get(username=username)
                if user.admin:
                    return f(user, *args, **kwargs)
                return {'message': 'Unauthorized'}, 401
            return {'message':"Please login first, your session might have expired"}, 401
        except Exception as e:
            return {'message': 'An error occured', 'error':str(e)},400
    return decorated