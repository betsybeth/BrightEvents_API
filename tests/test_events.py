from unittest import TestCase
from app import create_app
from app import db
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
            'author': '2',
            'location': 'nairobi'
        }

        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

    def registration(self):
        result = self.client.post(
            '/register',
            data=json.dumps(self.user),
            content_type='application/json')
        self.assertEqual(result.status_code, 201)

    def login(self):
        second_result = self.client.post(
            "/login",
            data=json.dumps(self.user),
            content_type='application/json')
        return second_result

    def test_create_event(self):
        self.registration()
        token_ = json.loads(self.login().data.decode())['token']
        print('>>>>', token_)
        result = self.client.post(
            '/create_event',
            data=json.dumps(self.event),
            content_type='application/json',
            headers = {
                'Authorization': token_
            })
        self.assertEqual(result.status_code, 201)

    def test_get_event_all(self):
        self.registration()
        token_ = json.loads(self.login().data.decode())['token']
        result = self.client.post('/create_event', data=json.dumps(self.event),content_type='application/json', headers = {
            'Authorization':token_
        })
        res = self.client.get('/events', data=json.dumps(self.event),content_type='application/json', headers = {
            'Authorization':token_
        })

        self.assertEqual(res.status_code, 200)
    def test_edit_event(self):
        self.registration()
        token_ = json.loads(self.login().data.decode())['token']
        result = self.client.post('/create_event', data=json.dumps(self.event), content_type='application/json', headers={
            'Authorization':token_
        })
        res = self.client.put('/events/<int:id>/', data=json.dumps(self.event), content_type='application/json',headers={
            'Authorization':token_
        })
        self.assertEqual(res.status_code, 200)

    def test_delete_event(self):
        self.registration()
        token_ = json.loads(self.login().data.decode())['token']
        result = self.client.post('/create_event', data=json.dumps(self.event), content_type='application/json', headers={
            'Authorization':token_
        })
        res = self.client.delete('/events/2/', content_type='application/json', headers={
            'Authorization':token_
        })
        self.assertEqual(res.status_code, 204)
