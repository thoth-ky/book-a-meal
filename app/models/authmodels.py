
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from sqlalchemy.orm import relationship
from sqlalchemy import (Table, Column, Integer, ForeignKey, String, Boolean,
                        Float, DateTime)
# local imports
from .models import Order, Meal
from .base import BaseModel


class User(BaseModel):
    """General user details"""
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    admin = Column(Boolean, default=False)
    super_user = Column(Boolean, default=False)
    orders = relationship('Order', backref='owner', lazy=True, uselist=True)
    meals = relationship('Meal', backref='caterer', lazy=True, uselist=True)
    is_active = Column(Boolean, default=True)

    def __init__(self, username, email, password):
        '''necessary to avoid setting admins directly'''
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.admin = False
        self.is_active = True

    def validate_password(self, password):
        '''check if user password is correct'''
        return check_password_hash(self.password_hash, password)

    def view(self):
        '''display user informtion, hide sensitive values'''
        user = self.make_dict()
        user['password_hash'] = '*'*10
        return user
        
    def generate_token(self):
        '''generate access_token, validity is period of time before it
        becomes invalid'''
        validity = current_app.config.get('TOKEN_VALIDITY')
        payload = {
            'exp': datetime.utcnow() + timedelta(minutes=validity),
            'iat': datetime.utcnow(),
            'username': self.username,
            'admin': self.admin,
            'superuser': self.super_user
        }
        token = jwt.encode(payload,
                            str(current_app.config.get('SECRET')),
                            algorithm='HS256'
                            )
        return token

    @staticmethod
    def decode_token(token):
        '''decode access token from authorization header'''
        try:
            payload = jwt.decode(
                token, str(current_app.config.get('SECRET')),
                algorithms=['HS256'])
            return payload
        except Exception:
            # the token is invalid, return an error string
            raise jwt.InvalidTokenError(
                "Invalid token. Please register or login")

    @staticmethod
    def promote_user(user):
        '''make user admin'''
        user.admin = True
        user.save()


class RevokedTokens(BaseModel):
    '''Keep a record of revoked tokens'''
    id = Column(Integer, primary_key=True)
    token = Column(String, index=True)



