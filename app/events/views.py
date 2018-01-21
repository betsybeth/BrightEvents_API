import re
from flask import Blueprint, jsonify, make_response, request
from flask.views import MethodView
from app.decorators.decorators import login_required
from app.models import Event

event_blueprint = Blueprint('event', __name__)


class Events(MethodView):
    """Event class handles events."""

    @login_required
    def post(self, user_id):
        """Creates an event."""
        json_dict = request.get_json()
        name = json_dict.get('name')
        description = json_dict.get('description')
        category = json_dict.get('category')
        date = json_dict.get('date')
        author = json_dict.get('author')
        location = json_dict.get('location')
        if name.isdigit():
            return make_response(
                jsonify({
                    'message': 'Name cannot be Integer'
                })), 400
        if name and name.strip():
            if Event.exist_event(user_id, name.strip(" ")):
                return make_response(
                    jsonify({
                        'message': 'Event already exists'
                    })), 409
            if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*', str(name)):
                response = {
                    'message': "name should not have special characters"
                }
                return make_response(jsonify(response)), 400
            if name and len(name.strip()) < 2:
                return make_response(
                    jsonify({
                        'message': 'Name is too short'
                    })), 400
            if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\'\"\{\}\[\]].*',
                        str(description)):
                response = {
                    'message': "description should not have special characters"
                }
                return make_response(jsonify(response)), 400
            if description and len(description.strip()) < 3:
                response = {'message': "description cannot be empty"}
                return make_response(jsonify(response)), 400
            if description and description.isdigit():
                return make_response(
                    jsonify({
                        'message': 'Description cannot be Integer'
                    })), 400
            elif description and len(description) > 200:
                return make_response(
                    jsonify({
                        'message':
                        'Description should not be long, maximum 200 words'
                    })), 400
            if category and category.isdigit():
                return make_response(
                    jsonify({
                        'message': 'Category cannot be Integer'
                    })), 400
            if  category and len(category.strip()) < 3:
                response = {'message': "category cannot be empty"}
                return make_response(jsonify(response)), 400
            if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*',
                        str(category)):
                response = {
                    'message': "category should not have special characters"
                }
                return make_response(jsonify(response)), 400
            elif category and  len(category) > 20:
                    return make_response(
                        jsonify({
                            'message': 'Category too long, maximum 20 letters'
                        })), 400

            if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*',
                        str(location)):
                response = {
                    'message': "location should not have special characters"
                }
                return make_response(jsonify(response)), 400
            if  location and len(location.strip()) < 3:
                response = {'message': "location cannot be empty"}
                return make_response(jsonify(response)), 400
            if location and location.isdigit():
                return make_response(
                    jsonify({
                        'message': 'Location cannot be Integer'
                    })), 400
            elif location and len(location) > 20:
                return make_response(
                    jsonify({
                        'message': 'Location too long, maximum 20 letters'
                    })), 400
            event = Event(
                name=name,
                description=description,
                category=category,
                date=date,
                author=user_id,
                location=location)
            event.save_event()
            response = {
                'id': event.id,
                'name': event.name,
                'description': event.description,
                'category': event.category,
                'date': event.date,
                'author': event.author,
                'location': event.location,
                'message': 'event successfully created'
            }
            return make_response(jsonify(response)), 201
        return make_response(
            jsonify({
                'message': 'name cannot be blank'
            })), 400

    @login_required
    def get(self, user_id, id=None):
        """Gets the created events."""
        if id is None:
            try:
                limit = int(request.args.get('limit', default=20, type=int))
                page = int(request.args.get('page', default=1, type=int))
            except TypeError:
                return make_response(
                    jsonify({
                        "error": "limit and page must be int"
                    })), 400
            if int(limit) > 6:
                limit = 6
            else:
                limit = int(limit)
            q = request.args.get('q', type=str)
            location = request.args.get('location')
            if location:
                event = Event.query.filter_by(author=user_id).first()
                if not event:
                    response = {'message': 'Event is not available'}
                    return make_response(jsonify(response)), 404
                events = Event.query.filter_by(author=user_id).filter(
                    Event.location.ilike(location))
                result = []
                result = [event.serialize() for event in events]
                return make_response(jsonify(result=result)), 200
            if q:
                event = Event.query.filter_by(author=user_id).first()
                if not event:
                    response = {'message': 'Event is not available'}
                    return make_response(jsonify(response)), 404
                events = Event.query.filter_by(author=user_id).filter(
                    Event.name.ilike(q))
                results = []
                for event in events:
                    event_search = {
                        'id': event.id,
                        'name': event.name,
                        'description': event.description,
                        'category': event.category,
                        'date': event.date,
                        'author': event.author,
                        'location': event.location,
                    }

                    results.append(event_search)
                return make_response(jsonify(results=results)), 200
            else:
                events = Event.query.filter_by(author=user_id).paginate(
                    int(page), int(limit), False)
                prev_page = ''
                next_page = ''
                pages = events.pages
                if events.has_prev:
                    prev_page = '/events/?limit={}&page={}'.format(
                        limit, events.prev_num)
                if events.has_next:
                    next_page = '/events/?limit={}&page={}'.format(
                        limit, events.next_num)
                result = []
                result = [event.serialize() for event in events.items]
                return make_response(
                    jsonify(
                        result=result,
                        prev_page=prev_page,
                        next_page=next_page,
                        pages=pages)), 200
        else:
            event = Event.query.filter_by(id=id).first()
            if not event:
                response = {'message': 'Event not available'}
                return make_response(jsonify(response)), 404
            else:
                response = event.serialize()
                return make_response(jsonify(response)), 200

    @login_required
    def put(self, id, user_id):
        """Edits the created  event."""
        event = Event.query.filter_by(author=user_id, id=id).first()
        json_dict = request.get_json()
        name = json_dict.get('name')
        description = json_dict.get('description')
        category = json_dict.get('category')
        date = json_dict.get('date')
        location = json_dict.get('location')
        if not event:
            response = {'message': 'no event available'}
            return make_response(jsonify(response)), 404
        if name and name.isdigit():
            return make_response(
                jsonify({
                    'message': 'Name cannot be Integer'
                 })), 400
        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*', str(name)):
            response = {'message': "name should not have special characters"}
            return make_response(jsonify(response)), 400
        if len(name.strip()) < 3:
            response = {'message': "name cannot be empty"}
            return make_response(jsonify(response)), 400
        if name and len(name.strip()) < 2:
            return make_response(jsonify({
                'message': 'Name is too short'
            })), 400
        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\'\"\{\}\[\]].*', str(description)):
            response = {
                'message': "description should not have special characters"
            }
            return make_response(jsonify(response)), 400
        if  description and len(description.strip()) < 3:
            response = {'message': "description cannot be empty"}
            return make_response(jsonify(response)), 400
        if description and description.isdigit():
            return make_response(
                jsonify({
                    'message': 'Description cannot be Integer'
                })), 400
        elif description and len(description) > 200:
            return make_response(
                jsonify({
                    'message':
                    'Description should not be long, maximum 200 words'
                })), 400
        if category and len(category.strip()) < 3:
            response = {'message': "category cannot be empty"}
            return make_response(jsonify(response)), 400
        if category and category.isdigit():
            return make_response(
                jsonify({
                    'message': 'Category cannot be Integer'
                })), 400
        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*', str(category)):
            response = {
                'message': "category should not have special characters"
            }
            return make_response(jsonify(response)), 400
        elif category and len(category) > 20:
            return make_response(
                jsonify({
                    'message': 'Category too long, maximum 20 letters'
                })), 400

        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*', str(location)):
            response = {
                'message': "location should not have special characters"
            }
            return make_response(jsonify(response)), 400
        if location and len(location.strip()) < 3:
            response = {'message': "location cannot be empty"}
            return make_response(jsonify(response)), 400
        if location and location.isdigit():
            return make_response(
                jsonify({
                    'message': 'Location cannot be Integer'
                })), 400
        elif location and len(location) > 20:
            return make_response(
                jsonify({
                    'message': 'Location too long, maximum 20 letters'
                })), 400
        event.name = name
        event.description = description
        event.category = category
        event.date = date
        event.location = location
        event.save_event()
        response = event.serialize()
        return make_response(jsonify(response)), 200

    @login_required
    def delete(self, user_id, id):
        """Delete an event according to the event id given."""
        events = Event.query.filter_by(id=id).first()
        if not events:
            response = {'message': 'event doesnt exist matching the id'}
            return make_response(jsonify(response)), 404
        else:
            events.delete_event()
            response = {'message': 'event deleted'}
            return make_response(jsonify(response)), 200


event_blueprint.add_url_rule(
    '/create_event', view_func=Events.as_view('event'), methods=['POST'])
event_blueprint.add_url_rule(
    '/events', view_func=Events.as_view('events'), methods=['GET'])
event_blueprint.add_url_rule(
    '/events/<int:id>/',
    view_func=Events.as_view('view_events'),
    methods=['DELETE', 'PUT', 'GET'])
