from unittest import TestCase
from app import create_app
from app.models import db
import json
from .base_file import registration, authorization


class TestEvents(TestCase):

    def setUp(self):
        self.app = create_app('Testing')
        self.client = self.app.test_client()
        self.user = {
            'name': 'testexample',
            'email': 'test@email.com',
            'password': '123456789',
            'confirm':'123456789'
        }
        self.event = {
            'name': 'talanta',
            'description': 'awesome',
            'category': 'social',
            'date': '2018-6-18',
            'location': 'nairobi'
        }

        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_create_event(self):
        """Test if an event has been created."""
        registration(self)
        result = self.client.post(
            '/create-event',
            data=json.dumps(self.event),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.assertEqual(result.status_code, 201)

    def test_invalid_event_name(self):
        """Test if event name has special \
        characters used  when creating and editing."""
        registration(self)
        event_details = {'name': '##$$$'}
        result = self.client.post(
            '/create-event',
            data=json.dumps(event_details),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.client.post(
            '/create-event',
            data=json.dumps(self.event),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        response = self.client.put(
            '/events/1/',
            data=json.dumps(event_details),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.assertIn('name should not have special characters',
                      str(result.data))
        self.assertIn('name should not have special characters',
                      str(response.data))
        self.assertEqual(result.status_code, 400)
        self.assertEqual(response.status_code, 400)

    def test_invalid_event_name_number(self):
        """Test if event name has numbers used when creating and editing."""
        registration(self)
        event_details = {'name': 12345}
        result = self.client.post(
            '/create-event',
            data=json.dumps(event_details),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.client.post(
            '/create-event',
            data=json.dumps(self.event),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        response = self.client.put(
            '/events/1/',
            data=json.dumps(event_details),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.assertIn('name cannot be number', str(result.data))
        self.assertIn('name cannot be number', str(response.data))
        self.assertEqual(result.status_code, 400)
        self.assertEqual(response.status_code, 400)

    def test_invalid_event_name_string_number(self):
        """Test if event name has string numbers \
         used  when creating and editing."""
        registration(self)
        event_details = {'name': '12345'}
        result = self.client.post(
            '/create-event',
            data=json.dumps(event_details),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.client.post(
            '/create-event',
            data=json.dumps(self.event),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        response = self.client.put(
            '/events/1/',
            data=json.dumps(event_details),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.assertIn('name cannot be integer', str(result.data))
        self.assertIn('Name cannot be Integer', str(response.data))
        self.assertEqual(result.status_code, 400)
        self.assertEqual(response.status_code, 400)

    def test_invalid_event_location(self):
        """Test if event location has special \
        characters used when creating and editing."""
        registration(self)
        event_details = {'name': 'talanta', 'location': '##$$$'}
        result = self.client.post(
            '/create-event',
            data=json.dumps(event_details),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.client.post(
            '/create-event',
            data=json.dumps(self.event),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        response = self.client.put(
            '/events/1/',
            data=json.dumps(event_details),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.assertIn('location should not have special characters',
                      str(result.data))
        self.assertIn('location should not have special characters',
                      str(response.data))
        self.assertEqual(result.status_code, 400)
        self.assertEqual(response.status_code, 400)

    def test_invalid_event_description_number(self):
        """Test if event description has \
         numbers used when creating and editing."""
        registration(self)
        event_details = {'name': 'talanta', "description": '12346976'}
        result = self.client.post(
            '/create-event',
            data=json.dumps(event_details),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })

        self.client.post(
            '/create-event',
            data=json.dumps(self.event),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        response = self.client.put(
            '/events/1/',
            data=json.dumps(event_details),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.assertIn('Description cannot be Integer', str(result.data))
        self.assertIn('Description cannot be Integer', str(response.data))
        self.assertEqual(result.status_code, 400)
        self.assertEqual(response.status_code, 400)

    def test_invalid_event_category(self):
        """Test if event category has special \
        characters used  when creating and editing."""
        registration(self)
        event_details = {'name': 'talanta', 'category': "asd$%@@@"}
        result = self.client.post(
            '/create-event',
            data=json.dumps(event_details),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.assertIn('category should not have special characters',
                      str(result.data))
        self.assertEqual(result.status_code, 400)

    def test_invalid_event_location_number(self):
        """Test if event location has \
        numbers used when creating and editing."""
        registration(self)
        event_details = {'name': 'talanta', "location": '12346976'}
        result = self.client.post(
            '/create-event',
            data=json.dumps(event_details),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.assertIn('Location cannot be Integer', str(result.data))
        self.assertEqual(result.status_code, 400)

    def test_already_event_exist(self):
        """Test if event already exists."""
        registration(self)
        self.client.post(
            '/create-event',
            data=json.dumps(self.event),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        res = self.client.post(
            '/create-event',
            data=json.dumps(self.event),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.assertIn('Event already exists due to the same name', str(
            res.data))
        self.assertEqual(res.status_code, 409)

    def test_if_event_available_viewing(self):
        """Test if event exist before viewing."""
        registration(self)
        result = self.client.get(
            '/events/2',
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.assertIn('This event is not available', str(result.data))
        self.assertEqual(result.status_code, 404)

    def test_get_event_all(self):
        """Test if you can view all event"""
        registration(self)
        self.client.post(
            '/create-event',
            data=json.dumps(self.event),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        res = self.client.get(
            '/events',
            data=json.dumps(self.event),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.assertEqual(res.status_code, 200)

    def test_get_public_events(self):
        """Test if you can view the events publicly."""
        res = self.client.get(
            '/public-events',
            data=json.dumps(self.event),
            content_type='application/json')
        self.assertEqual(res.status_code, 200)

    def test_get_event_by_id(self):
        """Test if you can get an event by it's Id."""
        registration(self)
        result = self.client.post(
            '/create-event',
            data=json.dumps(self.event),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        result_in_json = json.loads(result.data.decode())
        res = self.client.get(
            '/events/{}/'.format(result_in_json['id']),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.assertEqual(res.status_code, 200)

    def test_edit_event(self):
        """Test if event can be edited."""
        registration(self)
        new_data = {
            'name': 'eventname',
            'description': 'awesome',
            'category': 'social',
            'date': '12/9/20',
            'location': 'kisumu'
        }
        self.client.post(
            '/create-event',
            data=json.dumps(self.event),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        res = self.client.put(
            '/events/1/',
            data=json.dumps(new_data),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.assertEqual(res.status_code, 200)

    def test_delete_event(self):
        """Test if you can delete an event."""
        registration(self)
        self.client.post(
            '/create-event',
            data=json.dumps(self.event),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        res = self.client.delete(
            '/events/1/',
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.assertEqual(res.status_code, 200)

    def test_event_exist_after_delete(self):
        """test if the event already deleted is available"""
        registration(self)
        self.client.post(
            '/create-event',
            data=json.dumps(self.event),
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.client.delete(
            '/events/1/',
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        res = self.client.delete(
            '/events/1/',
            content_type='application/json',
            headers={
                'Authorization': authorization(self)
            })
        self.assertEqual(res.status_code, 404)
