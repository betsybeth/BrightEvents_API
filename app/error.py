from flask import jsonify, make_response


def not_found(error):
    """Handle 404 error."""
    return make_response(
        jsonify({
            "message": "Sorry the url does not exists"
        })), 404


def bad_request(e):
    """Check for error 400."""
    return make_response(
        jsonify({
            "message":
            " {} Bad request. Check your inputs and try again".format(e)
        })), 400


def internal_server_error(e):
    """Handle 500 error."""
    return make_response(
        jsonify({
            "message":
            "{} oops! something went wrong with the application".format(e)
        })), 500


def not_allowed(error):
    """Handle 405 error."""
    return make_response(
        jsonify({
            "message": "Sorry the method is not allowed"
        })), 405
