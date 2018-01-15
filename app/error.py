from flask import jsonify


def not_found(error):
    """Handle 404 error."""
    response = jsonify({"message": "Sorry the url does not exists"})
    response.status_code = 404
    return response


def handle_server_error(error):
    """Handle 500 error."""
    response = jsonify({
        "message":
        "oops! something went wrong with the application"
    })
    response.status_code = 500
    return response


def not_allowed(error):
    """Handle 405 error."""
    response = jsonify({"message": "Sorry the method is not allowed"})
    response.status_code = 405
    return response
