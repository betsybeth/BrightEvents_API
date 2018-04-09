from app import create_app
from app.models import db
import json



user = {
    'name': 'testexample',
    'email': 'test@email.com',
    'password': '123456789',
    'confirm':'123456789'
}
event = {
    'name': 'talanta',
    'description': 'awesome',
    'category': 'social',
    'date': '12/9/19',
    'location': 'nairobi'
}

def registration(self):
    """Helper method."""
    result = self.client.post(
        '/register',
        data=json.dumps(user),
        content_type='application/json')
    return result

def login(self):
    """Helper method."""
    second_result = self.client.post(
        "/login",
        data=json.dumps(user),
        content_type='application/json')
    return second_result

def authorization(self):
    """Authorization helper method."""
    token_ = json.loads(login(self).data.decode())['token']
    return token_
