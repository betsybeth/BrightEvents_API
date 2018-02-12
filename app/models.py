from datetime import datetime, timedelta
import jwt
import re
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """User database class."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    events = db.relationship(
        'Event',
        backref="users",
        lazy="dynamic",
        order_by="Event.id",
        cascade="all, delete-orphan")

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)

    @staticmethod
    def validate_email(email):
        return bool(re.match(r"([\w\.-]+)@([\w\.-]+)(\.[\w\.]+$)", email))

    def validate_password(self, password):
        """Checks the password against the hash password."""
        return check_password_hash(self.password, password)

    def generate_token(self, user_id):
        """Generate a token for authenication return String."""
        try:
            payload = {
                "exp": datetime.utcnow() + timedelta(minutes=100),
                "iat": datetime.utcnow(),
                "sub": user_id
            }

            jwt_string = jwt.encode(
                payload, current_app.config['SECRET'], algorithm='HS256')
            return jwt_string
        except Exception as e:
            return str(e)

    @staticmethod
    def decoding_token(token_auth):
        """Decodes a token and return String|Integer."""
        try:
            payload = jwt.decode(token_auth, current_app.config['SECRET'])
            blacklisted_token = BlackList.check_token(token_auth)
            if blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    def save_user(self):
        """Addes a user to the database"""
        db.session.add(self)
        db.session.commit()

    def serialize(self):
        """Returns the user as a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'password': self.password
        }


class Event(db.Model):
    """ Event database class."""
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    date_of_event = db.Column(db.DateTime)
    author = db.Column(db.Integer, db.ForeignKey(User.id))
    location = db.Column(db.String(80), nullable=False)
    rsvps = db.relationship(
        'Rsvp',
        backref="events",
        order_by="Rsvp.event_id",
        cascade="all, delete-orphan")

    def __init__(self, name, description, category, date_of_event, author,
                 location):
        self.name = name
        self.description = description
        self.category = category
        self.date_of_event = date_of_event
        self.author = author
        self.location = location

    def save_event(self):
        """Addes an event and stores it in the database."""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def validate_date(date_of_event):
        try:
            date = datetime.strptime(date_of_event, '%d-%m-%y').date()
        except ValueError:
            return 'you have entered the date format,date should be DD-MM-YY'
        if date < date.today():
            return ' event cannot have the previous date'
        return date_of_event

    @staticmethod
    def exist_event(user_id, date_of_event):
        """Checks if an exist exists."""
        event = Event.query.filter_by(
            author=user_id, date_of_event=date_of_event).first()
        if event:
            return True
        return False

    @staticmethod
    def get_all_event(user_id):
        """Gets all the events according to a particular user."""
        return Event.query.filter_by(author=user_id).all()

    def delete_event(self):
        """Deletes an event."""
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """Returns the event as a dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'date': self.date_of_event,
            'author': self.author,
            'location': self.location
        }


class Rsvp(db.Model):
    """ Rsvp database class"""
    __tablename__ = "rsvps"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    phone_no = db.Column(db.Integer, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey(Event.id))
    category = db.Column(db.String(80), nullable=False)

    def __init__(self, name, email, phone_no, event_id, category):
        self.name = name
        self.email = email
        self.phone_no = phone_no
        self.event_id = event_id
        self.category = category

    def save_rsvp(self):
        """Adds a rsvp to the database"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all_rsvp(event_id):
        """Gets all the rsvp according to a particular eventid."""
        return Rsvp.query.filter_by(event_id=event_id).all()

    def delete_rsvp(self):
        """Deletes a rsvp of the event."""
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """Returns the rsvp as a dictionary."""
        return {
            'name': self.name,
            'email': self.email,
            'phone_no': self.phone_no,
            'category': self.category,
            'event_id': self.event_id
        }


class BlackList(db.Model):
    """Class that handles blacklisting of tokens."""
    __tablename__ = "blacklist_token"

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(
        db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.now()

    def save_token(self):
        """Saves the token to the database."""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def check_token(auth_token):
        blacklist_token = BlackList.query.filter_by(
            token=str(auth_token)).first()
        if blacklist_token:
            return True

        return False

    def serialize(self):
        """Returns the token as a dictionary."""
        return {'token': self.token, 'blacklisted_no': self.blacklisted_on}
