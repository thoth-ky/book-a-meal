'''Set environment specific configurations here'''
import os


class Config:
    '''parent configuration class, contains all general configuration settings'''
    DEBUG = False
    SECRET = os.getenv('SECRET')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_USER = os.getenv('DB_USER')
    DB_NAME = os.getenv('DB_NAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    ORDER_EDITS_UPTO = os.getenv('ORDER_EDITS_UPTO')
    SQLALCHEMY_DATABASE_URI = 'postgresql://127.0.0.1:5433/{}'.format(
        DB_USER, DB_PASSWORD, DB_NAME)

    # mail server configs
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    MAIL_USERNAME = os.getenv('MAIL_USERNAME') or None
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD') or None
    ADMINS = ['jmutukudeveloper@gmail.com']
    MAIL_DEFAULT_SENDER = 'admin@bam.com'

    TOKEN_VALIDITY = int(os.getenv('TOKEN_VALIDITY'))

    # celery configs
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

class DevelopmentConfig(Config):
    '''Configurations for development. contains configuration settings specific to development'''
    DEBUG = True


class TestingConfig(Config):
    '''Configuration settings specific to testing environment'''
    DEBUG = True
    ORDER_EDITS_UPTO = 100
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class ProductionConfig(Config):
    '''Configuration settings specific to production environment'''
    DEBUG = False
    TESTING = False

config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production':ProductionConfig
}