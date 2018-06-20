'''Authentication decorators'''
import json

from functools import wraps
from flask import request, current_app
# local imports
from ..models.authmodels import User, RevokedTokens

class AuthorisationError(Exception):
    pass


def get_payload():
    '''get access token and decode it to get payload'''
    try:
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(' ')[1]
        if access_token and not RevokedTokens.get(token=access_token):
            return User.decode_token(access_token)
        raise AuthorisationError('Token has been revoked')
    except Exception as err:
        return 'Authorization Token not found or invalid!'


def token_required(func):
    '''checks user have valid tokens'''
    @wraps(func)
    def decorated(*args, **kwargs):
        '''decorator'''
        payload = get_payload()
        if isinstance(payload, str):
            return {'error': payload, 'message': 'Unauthorized'}, 401
        username = payload['username']
        user = User.get(username=username)
        # pragma: no cover
        return func(user=user, *args, **kwargs)
    return decorated


def admin_token_required(func):
    '''check users have valid tokens and they have admin property'''
    @wraps(func)
    def decorated(*args, **kwargs):
        '''decorator'''
        payload = get_payload()
        if isinstance(payload, str):
            return {'error': payload, 'message': 'Unauthorized'}, 401
        user_name, admin = payload['username'], payload['admin']
        user = User.get(username=user_name)
        if admin is True:
            # pragma: no cover
            return func(user=user, *args, **kwargs)
        # pragma: no cover
        return {'message': 'Unauthorized'}, 401
    return decorated


def super_admin_required(func):
    '''check users have valid tokens and they have admin property'''
    @wraps(func)
    def decorated(*args, **kwargs):
        '''decorator'''
        payload = get_payload()
        if isinstance(payload, str):
            return {'error': payload, 'message': 'Unauthorized'}, 401
        superuser = payload['superuser']
        if superuser is True:  # pragma: no cover
            return func(*args, **kwargs)
        return {'message': 'Unauthorized'}, 401  # pragma: no cover
    return decorated
