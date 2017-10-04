import os
from os.path import join, abspath, dirname
from dotenv import load_dotenv


def configure_env():
    # Configure environment variables
    dotenv_path = join(abspath(join(dirname(__file__), "..")), '.env')
    load_dotenv(dotenv_path, verbose=True)


class Config(object):
    """Parent configuration class."""
    DEBUG = False

    # Cross-Site request forgery
    CSRF_ENABLED = True

    # generate random 24 character secret key
    SECRET = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.getenv('db_url')


class DevelopmentConfig(Config):
    """Configurations for Development environment"""
    DEBUG = True


class TestingConfig(Config):
    """Configurations for testing. Uses a separate database for testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = \
        'postgresql://test_user:123456@localhost/test_db'
    DEBUG = True


class StagingConfig(Config):
    """Configurations for Staging."""
    DEBUG = True


class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


configurations = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
}
