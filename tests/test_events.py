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

    def test_create_event(self):
        """Test if an event has been created."""
        self.registration()
        token_ = json.loads(self.login().data.decode())['token']
        result = self.client.post(
            '/create_event',
            data=json.dumps(self.event),
            content_type='application/json',
            headers={
                'Authorization': token_
            })
        self.assertEqual(result.status_code, 201)

    def test_already_event_exist(self):
        """Test if event already exists."""
        self.registration()
        token_ = json.loads(self.login().data.decode())['token']
        result = self.client.post(
            '/create_event',
            data=json.dumps(self.event),
            content_type='application/json',
            headers={
                'Authorization': token_
            })
        self.assertEqual(result.status_code, 201)
        res = self.client.post(
            '/create_event',
            data=json.dumps(self.event),
            content_type='application/json',
            headers={
                'Authorization': token_
            })
        self.assertIn('Event already exists', str(res.data))
        self.assertEqual(res.status_code, 409)

    def test_if_event_available_viewing(self):
        """Test if event exist before viewing."""
        self.registration()
        token_ = json.loads(self.login().data.decode())['token']
        result = self.client.get(
            '/events/2',
            content_type='application/json',
            headers={
                'Authorization': token_})
        self.assertIn('Event not available', str(result.data))
        self.assertEqual(result.status_code, 404)
    def test_get_event_all(self):
        """Test if you can view all events"""
        self.registration()
        token_ = json.loads(self.login().data.decode())['token']
        result = self.client.post(
            '/create_event',
            data=json.dumps(
                self.event),
            content_type='application/json',
            headers={
                'Authorization': token_})
        res = self.client.get(
            '/events',
            data=json.dumps(
                self.event),
            content_type='application/json',
            headers={
                'Authorization': token_})

        self.assertEqual(res.status_code, 200)

    def test_get_event_by_id(self):
        """Test if you can get an event by it's Id."""
        self.registration()
        token_ = json.loads(self.login().data.decode())['token']
        result = self.client.post(
            '/create_event',
            data=json.dumps(
                self.event),
            content_type='application/json',
            headers={
                'Authorization': token_})
        result_in_json = json.loads(result.data.decode())
        res = self.client.get(
            '/events/{}/'.format(
                result_in_json['id']),
            content_type='application/json',
            headers={
                'Authorization': token_})
        self.assertEqual(res.status_code, 200)

    def test_edit_event(self):
        """Test if event can be edited."""
        self.registration()
        token_ = json.loads(self.login().data.decode())['token']
        self.new_data = {
            'name': 'eventname',
            'description': 'awesome',
            'category': 'social',
            'date': '12/9/20',
            'location': 'kisumu'
        }
        result = self.client.post(
            '/create_event',
            data=json.dumps(
                self.event),
            content_type='application/json',
            headers={
                'Authorization': token_})
        self.assertEqual(result.status_code, 201)
        res = self.client.put(
            '/events/1/',
            data=json.dumps(
                self.new_data),
            content_type='application/json',
            headers={
                'Authorization': token_})
        self.assertEqual(res.status_code, 200)

    def test_delete_event(self):
        """Test if you can delete an event."""
        self.registration()

        token_ = json.loads(self.login().data.decode())['token']
        result = self.client.post(
            '/create_event',
            data=json.dumps(
                self.event),
            content_type='application/json',
            headers={
                'Authorization': token_})
        res = self.client.delete(
            '/events/1/',
            content_type='application/json',
            headers={
                'Authorization': token_})
        self.assertEqual(res.status_code, 200)

    def test_event_exist_after_delete(self):
        """test if the event to be deleted is available"""
        self.registration()

        token_ = json.loads(self.login().data.decode())['token']
        result = self.client.post(
            '/create_event',
            data=json.dumps(
                self.event),
            content_type='application/json',
            headers={
                'Authorization': token_})
        res = self.client.delete(
            '/events/1/',
            content_type='application/json',
            headers={
                'Authorization': token_})
        self.assertEqual(res.status_code, 200)
        second_result = self.client.delete(
            '/events/1/',
            content_type='application/json',
            headers={
                'Authorization': token_})
        self.assertEqual(second_result.status_code, 404)
