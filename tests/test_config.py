from unittest import TestCase



class TestDevelopmentConfig(TestCase):
    def create_app():
        app.config.from_object(app.config.DevelopmentConfig)

    def test_is_development(self):
        self.assertTrue(app.config['DEBUG'] is True)
        self.assertFalse(current_app is None)
        self.assertTrue(app.config[SQLALCHEMY_DATABASE_URI] ==
                        "postgresql://postgres:postgres@localhost/flask_api")


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object(app.config.TestingConfig)
        return app

    def test_app_is_testing(self):
        self.assertTrue(app.config['DEBUG'] is True)
        self.assertTrue(app.config['SQLALCHEMY_DATABASE_URI']
                        == 'postgresql://postgres:postgres@localhost/test_db')
