import os


DATABASE_URI = 'postgresql://postgres:user123*-+@localhost/flask_api'


class Config(object):
    """Parent configuration class."""
    DEBUG = False

    # Cross-Site request forgery
    CSRF_ENABLED = True

    # generate random 24 character secret key
    SECRET = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = DATABASE_URI


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


configurations = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
}
