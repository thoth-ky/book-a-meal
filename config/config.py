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
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@127.0.0.1:5432/{}'.format(
        DB_USER, DB_PASSWORD, DB_NAME)

    # mail server configs
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 8025)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or None
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or None
    ADMINS = ['jmutukudeveloper@gmail.com']

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