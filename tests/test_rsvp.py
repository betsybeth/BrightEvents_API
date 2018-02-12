from unittest import TestCase
from app import create_app
from app.models import db
import json


class TestEvents(TestCase):

    def setUp(self):
        self.app = create_app('Testing')
        self.client = self.app.test_client()
        self.user = {
            'name': 'testexample',
            'email': 'test@email.com',
            'password': '123456789'
        }
        self.event = {
            'name': 'talanta',
            'description': 'awesome',
            'category': 'social',
            'date': '12/9/19',
            'location': 'nairobi'
        }
        self.rsvp = {
            'name': "nameexample",
            'email': 'example@test.com',
            'phone_no': '123456789',
            'category': 'guest'
        }

        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

    def registration(self):
        """Helper method."""
        result = self.client.post(
            '/register',
            data=json.dumps(self.user),
            content_type='application/json')
        self.assertEqual(result.status_code, 201)

    def login(self):
        """Helper method."""
        second_result = self.client.post(
            "/login",
            data=json.dumps(self.user),
            content_type='application/json')
        return second_result

    def authorization(self):
        """Authorization helper method."""
        token_ = json.loads(self.login().data.decode())['token']
        return token_

    def test_event_create(self):
        """Test if event can be created."""
        self.registration()
        result = self.client.post(
            '/create_event',
            data=json.dumps(self.event),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        self.assertEqual(result.status_code, 201)

    def test_rsvp_creation(self):
        """Test if rsvp can be created."""
        self.test_event_create()
        res = self.client.post(
            '/events/1/create_rsvp/',
            data=json.dumps(self.rsvp),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        self.assertEqual(res.status_code, 201)

    def test_rsvp_public(self):
        """Test if anyone can rsvp themselves to an event"""
        self.test_event_create()
        res = self.client.post(
            '/public_events/1/public_rsvps/',
            data=json.dumps(self.rsvp),
            content_type='application/json')
        self.assertEqual(res.status_code, 201)

    def test_invalid_rsvp_name_is_string_number(self):
        """Test if string number is used rsvp name."""
        self.test_event_create()
        rsvp_details = {"name": "12345"}
        res = self.client.post(
            '/events/1/create_rsvp/',
            data=json.dumps(rsvp_details),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })

        self.client.post(
            '/events/1/create_rsvp/',
            data=json.dumps(self.rsvp),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        response = self.client.put(
            '/events/1/rsvps/1/',
            data=json.dumps(rsvp_details),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        self.assertIn('name cannot be integer', str(res.data))
        self.assertIn('name cannot be integer', str(response.data))
        self.assertEqual(res.status_code, 400)
        self.assertEqual(response.status_code, 400)

    def test_invalid_rsvp_name_is_number(self):
        """Test if number is used rsvp name."""
        self.test_event_create()
        rsvp_details = {"name": 12345}
        res = self.client.post(
            '/events/1/create_rsvp/',
            data=json.dumps(rsvp_details),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })

        self.client.post(
            '/events/1/create_rsvp/',
            data=json.dumps(self.rsvp),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        response = self.client.put(
            '/events/1/rsvps/1/',
            data=json.dumps(rsvp_details),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        self.assertIn('name cannot be number', str(res.data))
        self.assertIn('name cannot be number', str(response.data))
        self.assertEqual(res.status_code, 400)
        self.assertEqual(response.status_code, 400)

    def test_invalid_rsvp_email(self):
        """Test if invalid rsvp email is used."""
        self.test_event_create()
        rsvp_details = {"email": "test.test"}
        res = self.client.post(
            '/events/1/create_rsvp/',
            data=json.dumps(rsvp_details),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        self.client.post(
            '/events/1/create_rsvp/',
            data=json.dumps(self.rsvp),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        response = self.client.put(
            '/events/1/rsvps/1/',
            data=json.dumps(rsvp_details),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        self.assertIn('invalid email', str(res.data))
        self.assertIn('Invalid email', str(response.data))
        self.assertEqual(res.status_code, 400)
        self.assertEqual(response.status_code, 400)

    def test_invalid_rsvp_name(self):
        """Test if invalid rsvp name is used."""
        self.test_event_create()
        rsvp_details = {"name": "@@@@"}
        res = self.client.post(
            '/events/1/create_rsvp/',
            data=json.dumps(rsvp_details),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        self.client.post(
            '/events/1/create_rsvp/',
            data=json.dumps(self.rsvp),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        response = self.client.put(
            '/events/1/rsvps/1/',
            data=json.dumps(rsvp_details),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        self.assertIn('name should not have special characters', str(res.data))
        self.assertIn('Name should not have special characters',
                      str(response.data))
        self.assertEqual(res.status_code, 400)
        self.assertEqual(response.status_code, 400)

    def test_rsvp_already_exists(self):
        """Test rsvp already exists."""
        self.test_event_create()
        self.client.post(
            '/events/1/create_rsvp/',
            data=json.dumps(self.rsvp),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        second_result = self.client.post(
            '/events/1/create_rsvp/',
            data=json.dumps(self.rsvp),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        self.assertIn('Rsvp already exists', str(second_result.data))
        self.assertEqual(second_result.status_code, 409)

    def test_get_all_rsvp(self):
        """Test if you can view all rsvp."""
        self.test_event_create()
        self.client.post(
            '/events/1/create_rsvp/',
            data=json.dumps(self.rsvp),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        res = self.client.get(
            '/events/1/rsvps/',
            data=json.dumps(self.rsvp),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        self.assertEqual(res.status_code, 200)

    def test_get_rsvp_by_id(self):
        """Test if you can get an Rsvp by it's Id."""
        self.test_event_create()
        response = self.client.post(
            '/events/1/create_rsvp/',
            data=json.dumps(self.rsvp),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        result_in_json = json.loads(response.data.decode())
        res = self.client.get(
            '/events/1/rsvps/{}'.format(result_in_json['id']),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        self.assertEqual(res.status_code, 200)

    def test_event_available_before_rsvp(self):
        """Test if event exist before rsvp creates."""
        self.registration()
        result = self.client.post(
            '/events/1/create_rsvp/',
            content_type='application/json',
            headers={
                'Authorization': self.authorization()})
        self.assertIn('This event is not available', str(result.data))
        self.assertEqual(result.status_code, 404)

    def test_event_available_before_get_rsvps(self):
        """Test if event exist before viewing rsvps."""
        self.registration()
        result = self.client.get(
            '/events/1/rsvps/',
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        self.assertIn('This event is not available', str(result.data))
        self.assertEqual(result.status_code, 404)

    def test_edit_rsvp(self):
        """Test if rsvp can be edited."""
        self.test_event_create()
        new_data = {
            'name': 'eventname',
            'email': 'person@person.com',
            'phone_no': '123458769',
            'category': 'social'
        }
        self.client.post(
            '/events/1/create_rsvp/',
            data=json.dumps(self.rsvp),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        res = self.client.put(
            '/events/1/rsvps/1/',
            data=json.dumps(new_data),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        self.assertEqual(res.status_code, 200)

    def test_delete_rsvp(self):
        """Test if event can be deleted."""
        self.test_event_create()
        self.client.post(
            '/events/1/create_rsvp/',
            data=json.dumps(self.rsvp),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        res = self.client.delete(
            '/events/1/rsvps/1/',
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        self.assertEqual(res.status_code, 200)

    def test_rsvp_exist_after_delete(self):
        """Test if rsvp exists after been deleted."""
        self.test_event_create()
        self.client.post(
            '/events/1/create_rsvp/',
            data=json.dumps(self.rsvp),
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        self.client.delete(
            '/events/1/rsvps/1/',
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        res = self.client.delete(
            '/events/1/rsvps/1/',
            content_type='application/json',
            headers={
                'Authorization': self.authorization()
            })
        self.assertEqual(res.status_code, 404)
