'''Set environment specific configurations here'''
import os


class Config:
    '''parent configuration class, contains all general configuration settings'''
    DEBUG = False


class DevelopmentConfig(Config):
    '''Configurations for development. contains configuration settings specific to development'''
    DEBUG = True


class TestingConfig(Config):
    '''Configuration settings specific to testing environment'''
    DEBUG = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
}