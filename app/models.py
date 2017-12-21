import datetime
import jwt
from app import db
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """User database class."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255))
    events = db.relationship(
        'Event',
        backref="users",
        order_by="Event.id",
        cascade="all, delete-orphan")

    def __init__(name, email, password):
        self.name = name
        self.password = generate_password_hash(password)

    def password_valid(self, password):
        """Checks the password against the hash password."""
        return check_password_hash(self.password, password)

    def encoding_token(self, user_id):
        """Generate a token for authenication return String."""
        try:
            payload = {
                "exp": datetime.utnow() + datetime.timedelta(seconds=10),
                "iat": datetime.datetime.utnow(),
                "sub": user_id
            }
            return jwt_encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256')
        except Exception as e:
            return e

    @staticmethod
    def decoding_token(token_auth):
        """Decodes a token and return String|Integer."""
        try:
            payload = jwt.decode(token_auth, app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    def save_user(self):
        """Addes a user to the database"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all_users():
        """Gets all the users."""
        return User.query.all()

    def __repr__(self):
        """Returns a representaion of the User class instance."""
        return "<User: {}>".format(self.name)


class Event(db.Model):
    """ Event database class."""
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    author = db.Column(db.String, db.ForeignKey(User.id))
    location = db.Column(db.String(255), nullable=False)
    rsvps = db.relationship(
        'Rsvp',
        order_by="RSVP.id",
        backref="events",
        order_by="Rsvp.id",
        cascade="all, delete-orphan")

    def __init__(name, description, category, date, author, location):
        self.name = name
        self.description = description
        self.category = category
        self.date = date
        self.author = author
        self.location = location

    def save_event(self):
        """Addes an event and stores it in the database."""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all_event(user_id):
        """Gets all the events according to a particular user."""
        return Event.query.filter_by(author=user_id).all()

    def delete_event(self):
        """Deletes an event."""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        """Returns a representaion of the Event class instance."""
        return "<Event: {}>".format(self.name)


class Rsvp(db.Model):
    """ Rsvp database class"""
    __tablename__ = "rsvps"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone_no = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(255), nullable=False)

    def __init__(name, email, phone_no, category, rsvp_id):
        self.name = name
        self.email = email
        self.phone_no = phone_no
        self.category = category
        self.rsvp_id = self.rsvp_id

    def save_rsvp(self):
        """Adds a rsvp to the database"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all_rsvp(rsvp_id):
        """Gets all the rsvp according to a particular eventid."""
        return Rsvp.query.filter_by(rsvp_id=rsvp_id).all()

    def delete_rsvp(self):
        """Deletes a rsvp of the event."""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        """Returns a representaion of the Rsvp class instance."""
        return "<Rsvp: {}>".format(self.name)
