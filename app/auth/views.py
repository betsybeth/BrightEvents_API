import re
import os
from datetime import datetime, timedelta
from flask.views import MethodView
from flask import Blueprint,current_app, make_response, request, jsonify, render_template, url_for
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from app.decorators.decorators import login_required
from app.models import User
from app.models import BlackList

auth_blueprint = Blueprint('auth', __name__)
mail = Mail()
SECRET = URLSafeTimedSerializer(os.getenv('SECRET'))


class Register(MethodView):
    """Register class handles authenication."""

    @staticmethod
    def post():
        """Registers user."""
        json_dict = request.get_json()
        name = json_dict.get('name')
        email = json_dict.get('email')
        password = json_dict.get('password')
        if name and email and password:
            if name and isinstance(name, int):
                return make_response(
                    jsonify({
                        'message': "name cannot be number"
                    })), 400
            if User.validate_email(email):
                if name.isdigit():
                    return make_response(
                        jsonify({
                            'message': "name cannot be integer"
                        })), 400
                if len(name.strip()) < 3:
                    return make_response(
                        jsonify({
                            'message': "name cannot be empty"
                        })), 400
                if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*',
                            name):
                    return make_response(
                        jsonify({
                            'message':
                            "name should not have special characters"
                        })), 400
                if len(password.strip()) < 3:
                    return make_response(
                        jsonify({
                            'message': "password cannot be empty"
                        })), 400
                if len(password) < 8:
                    return make_response(
                        jsonify({
                            'message': "password is too short"
                        })), 400
                try:
                    user = User(name=name, email=email, password=password)
                    user.authenticated = True

                    # msg = Message(sender = current_app.config.get('MAIL_USERNAME'),subject='Registration',
                    #           body='Thanks for registering with BritoEvento!',
                    #           recipients=[user.email])
                    msg = Message(
                            "RSVP to an Event",
                            sender='bethwambuimuniu@gmail.com',
                            recipients=[user.email])
                    msg.html = 'To Verify your Email Addres'

                    mail.send(msg)

                    user.save_user()
                    token_ = user.generate_token(user.id)
                    response = {
                        'message': 'successfully registered',
                        'token': token_.decode()
                    }
                    return make_response(jsonify(response)), 201
                except ValueError:
                    return make_response(jsonify({'message': 'Email already exists'})), 409
            return make_response(jsonify({'message': 'invalid email'})), 400
        return make_response(jsonify({'message': 'empty inputs'})), 400


class Login(MethodView):
    """Login class handles registered user login."""

    def post(self):
        """Login user."""
        json_dict = request.get_json()
        email = json_dict.get('email')
        password = json_dict.get('password')
        user = User.query.filter_by(email=email).first()
        if not user:
            return make_response(
                jsonify({
                    'message': 'you are not registered,please register'
                })), 400
        elif user and user.validate_password(password):
            token_ = user.generate_token(user.id)
            if token_:
                response = {
                    'message': 'you are successfully login',
                    'token': token_.decode()
                }
                return make_response(jsonify(response)), 200
        else:
            return make_response(
                jsonify({
                    'message': 'wrong email or password, please try again'
                })), 400


class Logout(MethodView):
    """Handle logout."""

    def post(self):
        """Logout a registered user."""
        auth_token = request.headers.get('Authorization')
        if auth_token:
            resp = User.decoding_token(auth_token)
            if not isinstance(resp, str):
                blacklist_token = BlackList(token=auth_token)
                try:
                    blacklist_token.save_token()
                    return make_response(
                        jsonify({
                            'message': 'successfully logout'
                        })), 200
                except Exception as e:
                    return make_response(jsonify({"message": e})), 400
            return make_response(jsonify({"message": resp})), 404
        return make_response(
            jsonify({
                "message": "Please provide a valid token"
            })), 403


class ResetPassword(MethodView):
    """Validates an email that is been used to reset password for an existing user,
        then the user is able to reset password in a secure way"""

    @staticmethod
    def post():
        json_dict = request.get_json()
        email = json_dict.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = SECRET.dumps(user.email, salt='reset_password')
            subject = "Reset Password"
            name = user.name
            link = url_for("auth.reset_password", token=token, _external=True)
            html = render_template("inline_reset.html", link=link)

            send_mail(to=user.email, subject=subject, html=html)

            return make_response(jsonify({
                'message': 'Check your email to reset your password.'
            })) ,200

        return make_response(jsonify({
            'message': 'Wrong Email or email does not exist.'
        })), 401

    @staticmethod
    def put(token):
        """Resets user password"""
        try:
            email = SECRET.loads(
                token, salt='reset-password',
                max_age=4000
            )

        except SignatureExpired:
            response = {
                'message': 'The token is expired!, confirm your e-mail again'
            }
            return make_response(jsonify(response)), 40
        user = User.query.filter_by(email=email).first()
        json_dict = request.get_json()
        new_password = json_dict.get('new_password')
        if user:
            user.password = generate_password_hash(new_password)
            user.save_user()
            response = {
                "message": 'Password reset successful',
                'new password': new_password
            }
            return make_response(jsonify(response)), 201


class ConfirmEmail(MethodView):
    """Handles email confirmation and checks if it is the right email and verifys"""

    @staticmethod
    def post():
        """Handle POST request for this view. Url ---> /api/auth/confirm"""
        json_dict = request.get_json()
        email = json_dict.get('email')
        user = User.query.filter_by(email=email).first()
        name = user.name
        if user:
            token = SECRET.dumps(user.email, salt='email-confirm')
            subject = "Email Confirmation"

            link = url_for("auth.confirm_email", token=token, _external=True)
            html = render_template("confirm_email.html", name=name,link=link)
            send_mail(to=user.email, subject=subject, html=html)

            response = {
                'message': 'check email to verify.'
            }
            return make_response(jsonify(response)), 200

        response = {
            'message': 'Wrong Email or user email does not exist.'
        }
        return make_response(jsonify(response)), 401

    @staticmethod
    def put(token):
        """Handles processing the unique link send to a user when they register and also confirming the token. """
        try:
            email = SECRET.loads(
                token, salt='email-confirm',
                max_age=4000
            )
        except SignatureExpired:
            return make_response(jsonify({
                'message': 'token is expired!, confirm your e-mail again'
            })),401

        user = User.query.filter_by(email=email).first()
        if user.email_confirmed:
            return make_response(jsonify({'Account already confirmed. Please login.'})),409
        else:
            user.email_confirmed = True
            user.email_confirmed_on = datetime.now()
            user.save_user()
            return make_response(jsonify({'Thank you for confirming your email address!'})),200



class ChangePassword(MethodView):
    """Change Password class handles an changing password."""

    @login_required
    def post(self, user_id):
        """change an existing password to a rememberable password."""
        json_dict = request.get_json()
        old_password = json_dict.get('old_password')
        new_password = json_dict.get("new_password")
        confirm_password = json_dict.get('confirm_password')
        user = User.query.filter_by(id=user_id).first()
        if old_password and user.validate_password(old_password):
            if len(new_password.strip()) < 3:
                return make_response(
                    jsonify({
                        'message': "password cannot be empty"
                    })), 400
            if len(new_password) < 8:
                return make_response(
                    jsonify({
                        'message': "password is too short"
                    })), 40
            if new_password == confirm_password:
                user.password = generate_password_hash(new_password)
                user.save_user()
                return make_response(
                    jsonify({
                        'message': 'password changed successfully'
                    })), 201
            return make_response(
                jsonify({
                    'message':
                    'new password  and confirm password should be equal'
                })), 400
        return make_response(jsonify({'message': 'wrong password'})), 403


auth_blueprint.add_url_rule(
    '/register', view_func=Register.as_view('register'), methods=['POST'])
auth_blueprint.add_url_rule(
    '/login', view_func=Login.as_view('login'), methods=['POST'])
auth_blueprint.add_url_rule(
    '/logout', view_func=Logout.as_view('logout'), methods=['POST'])
auth_blueprint.add_url_rule(
    '/confirm_email',
    view_func=ConfirmEmail.as_view('confirm_email'),
    methods=['POST', 'PUT'])
auth_blueprint.add_url_rule(
    '/reset-password',
    view_func=ResetPassword.as_view('reset_password'),
    methods=['POST', 'PUT'])
auth_blueprint.add_url_rule(
    '/change-password',
    view_func=ChangePassword.as_view('change-password'),
    methods=['POST'])
