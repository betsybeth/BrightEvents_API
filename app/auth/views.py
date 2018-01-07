from flask.views import MethodView
from flask import Blueprint, make_response, request, jsonify
from werkzeug.security import generate_password_hash
from app.models import User

auth_blueprint = Blueprint('auth', __name__)


class Register(MethodView):
    """Register class handles authenication."""

    def post(self):
        """Registers user."""
        json_dict = request.get_json()
        name = json_dict.get('name')
        email = json_dict.get('email')
        password = json_dict.get('password')
        if name and email and password:
            if User.validate_email(email):

                if name.strip() == "":
                    response = {'message': "invalid name"}
                    return make_response(jsonify(response)), 400

                if len(password) < 8:
                    response = {
                        'message': 'password  too short'
                    }
                    return make_response(jsonify(response)), 400
                user = User.query.filter_by(email=email).first()
                if user:
                    response = {
                        'message': 'email already exists,Please log in'}
                    return make_response(jsonify(response))
                user = User(name=name, email=email, password=password)
                user.save_user()
                token_ = user.generate_token(user.id)
                response = {
                    'message': 'successfully registered',
                    'token': token_.decode()
                }
                return make_response(jsonify(response)), 201
            return make_response(
                jsonify({'message': 'invalid name or email'})), 400
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
            response = {
                'message': 'you are not registered,please register'
            }
            return make_response(jsonify(response)), 400
        elif user and user.validate_password(password):
            token_ = user.generate_token(user.id)
            if token_:
                response = {
                    'message': 'you are successfully login',
                    'token': token_.decode()
                }
                return make_response(jsonify(response)), 200
        else:
            response = {
                'message': 'wrong email or password, please try again'
            }
            return make_response(jsonify(response)), 400


class Logout(MethodView):
    """Logout class"""

    def post(self):
        """Logout a registered user."""
        auth_token = request.headers.get('Authorization')
        if auth_token:
            resp = User.decoding_token(auth_token)
            return make_response(
                jsonify({'message': 'successfully logout'})), 200
        return make_response(
            jsonify({'messsage': 'wrong token,Please check you token if correct'})), 403


class ResetPassword(MethodView):
    """ResetPassword class handles resetting password."""

    def post(self):
        """Resets user password"""
        json_dict = request.get_json()
        email = json_dict.get('email')
        new_password = json_dict.get('new_password')
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(new_password)
            user.save_user()
            response = {
                "message": 'Password reset successful',
                'new password': new_password
            }
            return make_response(jsonify(response)), 201
        response = {'message': 'Invalid email'}
        return make_response(jsonify(response)), 400


class ChangePassword(MethodView):
    """Change Password class handles an changing password."""

    def post(self):
        """change an existing password to a rememberable password."""
        json_dict = request.get_json()
        email = json_dict.get('email')
        old_password = json_dict.get('old_password')
        new_password = json_dict.get("new_password")
        confirm_password = json_dict.get('confirm_password')
        user = User.query.filter_by(email=email).first()
        if old_password and user.validate_password(old_password):
            print('>>>>', old_password)
            if new_password == confirm_password:
                user.password = generate_password_hash(new_password)
                user.save_user()
                response = {'message': 'password changed successfully'}
                return make_response(jsonify(response)), 201
            return make_response(jsonify(
                {'message': 'new password  and confirm password should be equal'})), 400
        return make_response(jsonify({'message': 'invalid email'})), 403


auth_blueprint.add_url_rule(
    '/register',
    view_func=Register.as_view('register'),
    methods=['POST'])
auth_blueprint.add_url_rule(
    '/login',
    view_func=Login.as_view('login'),
    methods=['POST'])
auth_blueprint.add_url_rule(
    '/logout',
    view_func=Logout.as_view('logout'),
    methods=['POST'])
auth_blueprint.add_url_rule(
    '/reset-password',
    view_func=ResetPassword.as_view('reset_password'),
    methods=['POST'])
auth_blueprint.add_url_rule(
    '/change-password',
    view_func=ChangePassword.as_view('change-password'),
    methods=['POST'])
