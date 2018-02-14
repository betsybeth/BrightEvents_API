import os


class Config(object):
    """Base configuration class."""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv("SECRET")
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_SUPPRESS_SEND = False


class DevelopmentConfig(Config):
    """Development configuration class."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration class."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/test_db"


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


app_configuration = {
    "development": DevelopmentConfig,
    "Testing": TestingConfig,
    "production": ProductionConfig,
}
