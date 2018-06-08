"""Importation of modules."""
from unittest import TestCase
import json
from app import create_app
from app.models import db
from .base_file import registration, authorization


class TestAuthenication(TestCase):
    """Tests the authenication blueprints."""

    def setUp(self):
        self.app = create_app('Testing')
        self.client = self.app.test_client()
        self.user = {
            'name': 'testexample',
            'email': 'test@email.com',
            'password': '12345678',
            'confirm':'12345678'
        }

        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_user_registration(self):
        """Test if user can register."""
        result = self.client.post(
            '/register',
            data=json.dumps(self.user),
            content_type='application/json')
        self.assertIn('successfully registered', str(result.data))
        self.assertEqual(result.status_code, 201)

    def test_user_register_twice(self):
        """Test if user can be registered twice."""
        registration(self)
        self.assertIn('email already exists,Please log in',
                      str(registration(self).data))
        self.assertEqual(registration(self).status_code, 409)

    def test_invalid_name_used(self):
        """Test invalid name is empty."""
        user_data = {'name': ""}
        result = self.client.post(
            '/register',
            data=json.dumps(user_data),
            content_type='application/json')
        self.assertEqual(result.status_code, 400)
        self.assertIn('empty inputs', str(result.data))

    def test_name_invalid_number_used(self):
        """Test invalid name is entered as number."""
        user_data = {
            'name': 1234567,
            "password": self.user['password'],
            'email': self.user['email']
        }
        result = self.client.post(
            '/register',
            data=json.dumps(user_data),
            content_type='application/json')
        self.assertEqual(result.status_code, 400)
        self.assertIn('name cannot be number', str(result.data))

    def test_user_login(self):
        """Test if user can login."""
        self.test_user_registration()
        second_result = self.client.post(
            "/login",
            data=json.dumps(self.user),
            content_type='application/json')
        self.assertIn('you are successfully login', str(second_result.data))
        self.assertEqual(second_result.status_code, 200)

    def test_login_of_unregistered_user(self):
        """Test if the login user is registered."""
        result = self.client.post(
            "/login",
            data=json.dumps(self.user),
            content_type='application/json')
        self.assertIn('you are not registered,please register', str(
            result.data))
        self.assertEqual(result.status_code, 400)

    def test_invalid_password(self):
        """Test if invalid password is used when login."""
        registration(self)
        user_details = {'email': self.user['email'], 'password': '54321'}
        response = self.client.post(
            '/login',
            data=json.dumps(user_details),
            content_type='application/json')
        self.assertEqual(400, response.status_code)

    def test_invalid_email(self):
        """Test if invalid email is used when login."""
        user_details = {
            'email': 'wrong@email.com',
            'password': self.user['password']
        }
        response = self.client.post(
            '/login',
            data=json.dumps(user_details),
            content_type='application/json')
        self.assertIn('you are not registered,please register',
                      str(response.data))
        self.assertEqual(400, response.status_code)

    def test_change_password(self):
        """Test if user can  change password."""
        registration(self)
        user_details = {
            'old_password': '123456789',
            'new_password': '12345769',
            'confirm_password': '12345769'
        }
        second_result = self.client.post(
            "/change-password",
            data=json.dumps(user_details),
            headers={'Authorization': authorization(self)},
            content_type='application/json')
        self.assertIn('password changed successfully', str(second_result.data))
        self.assertEqual(201, second_result.status_code)

    def test_wrong_old_password(self):
        """Test if old password is wrong."""
        registration(self)
        user_details = {
            'old_password': '23467889934',
            'new_password': '12345769',
            'confirm_password': '12345769'
        }
        second_result = self.client.post(
            "/change-password",
            data=json.dumps(user_details),
            headers={'Authorization': authorization(self)},
            content_type='application/json')
        self.assertIn('wrong password', str(second_result.data))
        self.assertEqual(second_result.status_code, 403)

    def test_password_are_similar(self):
        """Test if the new password is similar to the confirm password."""
        registration(self)
        user_details = {
            'old_password': '123456789',
            'new_password': '12348769',
            'confirm_password': '12345769'
        }
        second_result = self.client.post(
            "/change-password",
            data=json.dumps(user_details),
            headers={'Authorization': authorization(self)},
            content_type='application/json')
        self.assertIn('new password  and confirm password should be equal',
                      str(second_result.data))
        self.assertEqual(400, second_result.status_code)

    def test_logout_user(self):
        """Test if registered user can logout."""
        registration(self)
        result = self.client.post(
            '/logout',
            headers={'Authorization': authorization(self)},
            content_type='application/json')
        self.assertIn('successfully logged out', str(result.data))
        self.assertEqual(result.status_code, 200)

    def test_reset_password(self):
        """Test if user can reset password."""
        registration(self)
        user_data = {
            "email": self.user['email'],
            'new_password': '09876543'
        }
        res = self.client.put(
            '/reset-password',
            data=json.dumps(user_data),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.assertEqual(res.status_code, 201)
        self.assertIn('Password reset successful', str(res.data))

    def test_invalid_reset_email(self):
        """Test if a wrong email is used when resetting password."""
        registration(self)
        user_data = {"email": 'test@el.com', 'new_password': '09876543'}
        res = self.client.post(
            '/reset-password',
            data=json.dumps(user_data),
            content_type='application/json')
        self.assertEqual(res.status_code, 400)
