'''Set environment specific configurations here'''
import os


class Config:
    '''parent configuration class, contains all general configuration settings'''
    DEBUG = False
    SECRET = os.getenv('SECRET')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_USER =  os.getenv('DB_USER')
    DB_NAME = os.getenv('DB_NAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@127.0.0.1:5432/{}'.format(DB_USER, DB_PASSWORD, DB_NAME)


class DevelopmentConfig(Config):
    '''Configurations for development. contains configuration settings specific to development'''
    DEBUG = True


class TestingConfig(Config):
    '''Configuration settings specific to testing environment'''
    DEBUG = True
    DB_USER =  os.getenv('DB_USER')
    TEST_DB_NAME = os.getenv('DB_NAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@127.0.0.1:5432/{}'.format(DB_USER, DB_PASSWORD, TEST_DB_NAME)


class ProductionConfig(Config):
	DEBUG = False
	TESTING = False

config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production':ProductionConfig
}