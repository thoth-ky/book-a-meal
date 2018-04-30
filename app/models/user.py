'''Model for User'''
from datetime import datetime, timedelta
import jwt
from flask import current_app


# local imports
from . import BaseModel


class User(BaseModel):
    """General user details"""

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.admin = False

    def __str__(self):
        '''String repr of the user objects'''
        return '<User: {}'.format(self.username)

    def validate_password(self, password):
        '''check if user password is correct'''
        return password == self.password

    def generate_token(self):
        '''generate access_token'''
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=120),
                'iat': datetime.utcnow(),
                'username': self.username,
            }
            token = jwt.encode(payload,
                               str(current_app.config.get('SECRET')),
                               algorithm='HS256'
                              )
            return token
        except Exception as err:
            return str(err)

    @staticmethod
    def decode_token(token):
        '''decode access token from authorization header'''
        try:
            payload = jwt.decode(
                token, str(current_app.config.get('SECRET')), algorithms=['HS256'])
            return payload['username']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return "Invalid token. Please register or login"

