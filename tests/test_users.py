from unittest import TestCase
from app import create_app
from app import db
import json


class TestAuthenication(TestCase):
    """Tests the authenication blueprints."""
    def setUp(self):
        self.app = create_app('Testing')
        self.client =self.app.test_client()
        self.user = {'name': 'testexample',
                     'email': 'test@email.com',
                     'password': '123456789'
                     }

        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_user_registration(self):
        result = self.client.post('/register', data=json.dumps(self.user),content_type='application/json')
        self.assertIn('successfully registered', str(result.data))
        self.assertEqual(result.status_code, 201)

    def test_user_register_once(self):
        result = self.client.post('/register', data=json.dumps(self.user),content_type='application/json')
        self.assertEqual(result.status_code, 201)
        second_result = self.client.post('/register', data=json.dumps(self.user),content_type='application/json' )
        self.assertIn('email already exists,Please log in', str(second_result.data))
        self.assertEqual(second_result.status_code, 409)

    def test_user_login(self):
        result= self.client.post('/register', data=json.dumps(self.user), content_type='application/json')
        second_result = self.client.post("/login", data=json.dumps(self.user), content_type='application/json')
        self.assertIn('you are successfully login', str(second_result.data))
        self.assertEqual(second_result.status_code, 200)
    def test_login_of_unregistered_user(self):
        result = self.client.post("/login", data=json.dumps(self.user), content_type='application/json')
        self.assertIn('you are not registered,please register', str(result.data))
        self.assertEqual(result.status_code, 400)
    def test_logout_user(self):
        second_result = self.client.post("/login", data=json.dumps(self.user), content_type='application/json')
        result = self.client.post("/logout", data=json.dumps(self.user), content_type='application/json')
        self.assertIn('successfully logout' , str(result.data))
        self.assertEqual(result.status_code,200)
    def test_reset_password(self):
        user_data = { "email":'test@email.com',
                        'new_password':'098765432'}
        result = self.client.post('/reset-password', data=json.dumps(user_data), content_type='application/json')
        self.assertEqual(result.status_code, 201)
        self.assertIn('Password reset successful', str(result.data))    
