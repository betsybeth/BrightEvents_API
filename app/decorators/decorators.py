import os
from flask import current_app,request, jsonify, make_response
from functools import wraps
from app.models import User


def login_required(func):
    """It modifyies the authenication token function in the database models."""

    @wraps(func)
    def decorator(*args, **kwargs):
        auth_token = request.headers.get('Authorization')
        if auth_token:
            kwargs['user_id'] = User.decoding_token(auth_token)
            if not isinstance(kwargs['user_id'], int):
                message = kwargs['user_id']
                response = {'message': message}
                return make_response(jsonify(response)), 401
        else:
            response = {
                "message": "Invalid token.Please register or login",
            }
            return make_response(jsonify(response)), 401
        return func(*args, **kwargs)

    return decorator
