import os

class Config(object):
    """Base configuration class."""
    DEBUG = False
    SECRET = os.getenv("SECRET")
    DATABASE_URI = os.getenv('DATABASE_URL')

class DevelopmentConfig(Config):
    """Development configuration class."""
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration class."""
    DEBUG = True
    DATABASE_URL ='postgresql://localhost/test_db'


app_configuration = {
    "development": DevelopmentConfig,
    "Testing": TestingConfig,
}
