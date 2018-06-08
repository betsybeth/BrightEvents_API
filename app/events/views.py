from datetime import datetime, timedelta
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
        date_of_event = json_dict.get('date_of_event')
        location = json_dict.get('location')
        if date_of_event:
            try:
                date = datetime.strptime(date_of_event, '%Y-%m-%d').date()
            except ValueError:
                return make_response(
                    jsonify({
                        'message':
                        'Incorect date format,date should be YYYY-MM-DD'
                    })), 400

            if date < date.today():
                return make_response(
                    jsonify({
                        'message': 'event cannot have the previous date'
                    })), 400

        if name and isinstance(name, int):
            return make_response(
                jsonify({
                    'message': "name cannot be number"
                })), 400
        if name and name.strip():
            if Event.exist_event(user_id, name):
                return make_response(
                    jsonify({
                        'message':
                        'Event already exists due to the same name'
                    })), 409
            if name.isdigit():
                return make_response(
                    jsonify({
                        'message': "name cannot be integer"
                    })), 400
            if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*',
                        str(name)):
                return make_response(
                    jsonify({  
                        'message':
                        "name should not have special characters"
                    })), 400
            if description and isinstance(description, int):
                return make_response(
                    jsonify({
                        'message': "description cannot be number"
                    })), 400
            if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*',
                        str(description)):
                return make_response(
                    jsonify({
                        'message':
                        "description should not have special characters"
                    })), 400
            if description and len(description.strip()) < 3:
                return make_response(
                   jsonify({
                        'message': "description cannot be empty"
                    })), 400
            if description and description.isdigit():
                return make_response(
                    jsonify({
                        'message': 'Description cannot be Integer'
                    })), 400
            if category and isinstance(category, int):
                return make_response(
                    jsonify({
                        'message': "category cannot be number"
                    })), 400
            if category and category.isdigit():
                return make_response(
                    jsonify({
                        'message': 'Category cannot be Integer'
                    })), 400
            if category and len(category.strip()) < 3:
                return make_response(
                    jsonify({
                        'message': "category cannot be empty"
                    })), 400
            if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*',
                        str(category)):
                return make_response(
                    jsonify({
                        'message':
                        "category should not have special characters"
                    })), 400
            if location and isinstance(location, int):
                return make_response(
                    jsonify({
                        'message': "location cannot be number"
                    })), 400
            if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*',
                        str(location)):
                return make_response(
                    jsonify({
                        'message':
                        "location should not have special characters"
                    })), 400
            if location and len(location.strip()) < 3:
                return make_response(
                    jsonify({
                        'message': "location cannot be empty"
                    })), 400
            if location and location.isdigit():
                return make_response(
                    jsonify({
                        'message': 'Location cannot be Integer'
                    })), 400
            event = Event(
                name=name,
                description=description,
                category=category,
                date_of_event=date_of_event,
                author=user_id,
                location=location)
            event.save_event()
            response = {
                'id': event.id,
                'name': event.name,
                'description': event.description,
                'category': event.category,
                'date_of_event': event.date_of_event,
                'author': event.author,
                'location': event.location,
                'message': 'event successfully created'
            }
            return make_response(jsonify(response)), 201
        return make_response(jsonify({'message': 'name cannot be blank'})), 400

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
                    return make_response(
                        jsonify({
                            'message': 'This event is not available'
                        })), 404
                events = Event.query.filter_by(author=user_id).filter(
                    Event.location.ilike(location))
                result = []
                result = [evet.serialize() for evet in events]
                return make_response(jsonify(result=result)), 200
            if q:
                event = Event.query.filter_by(author=user_id).first()
                if not event:
                    return make_response(
                        jsonify({
                            'message': 'This event is not available'
                        })), 404
                events = Event.query.filter_by(author=user_id).filter(
                    Event.name.ilike("%" + q + "%"))
                result = []
                for event in events:
                    event_search = {
                        'id': event.id,
          
                        'name': event.name,
                        'description': event.description,
                        'category': event.category,
          
                        'date_of_event': event.date_of_event,
                        'author': event.author,
                        'location': event.location,
                    }

                    result.append(event_search)
                return make_response(jsonify(result=result)), 200
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
                results = []
                for event in events.items:
                    event_found = {
                        'id': event.id,
                        'name': event.name,
                        'description': event.description,
                        'category': event.category,
                        'date_of_event': event.date_of_event,
                        'author': event.author,
                        'location': event.location,
                    }

                    results.append(event_found)
                return make_response(
                    jsonify(
                        results=results,
                        prev_page=prev_page,
                        next_page=next_page,
                        pages=pages)), 200
        else:
            event = Event.query.filter_by(id=id).first()
            if not event:
                return make_response(
                    jsonify({
                        'message': 'This event is not available'
                    })), 404
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
        date_of_event = json_dict.get('date_of_event')
        location = json_dict.get('location')
        if not event:
            return make_response(
                jsonify({
                    'message': 'This event is not available'
                })), 404
        if date_of_event:
            try:
                date = datetime.strptime(date_of_event, '%Y-%m-%d').date()
            except ValueError:
                return make_response(
                    jsonify({
                        'message':
                        'Incorect date format,date should be YYYY-MM-DD'
                    })), 400
        
        if name and isinstance(name, int):
            return make_response(
                jsonify({
                    'message': "name cannot be number"
                })), 400
        if name and name.isdigit():
            return make_response(
                jsonify({
                    'message': 'Name cannot be Integer'
                })), 400
        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*', str(name)):
            return make_response(
                jsonify({
                    'message': "name should not have special characters"
                })), 400
        if len(name.strip()) < 3:
            return make_response(jsonify({
                'message': "name cannot be empty"
            })), 400
        if name and len(name.strip()) < 2:
            return make_response(jsonify({
                'message': 'Name is too short'
            })), 400
        if description and isinstance(description, int):
            return make_response(
                jsonify({
                    'message': "description cannot be number"
                })), 400
        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\'\"\{\}\[\]].*',
                    str(description)):
            return make_response(
                jsonify({
                    'message':
                    "description should not have special characters"
                })), 400
        if description and len(description.strip()) < 3:
            return make_response(
                jsonify({
                    'message': "description cannot be empty"
                })), 400
        if description and description.isdigit():
            return make_response(
                jsonify({
                    'message': 'Description cannot be Integer'
                })), 400
        if category and isinstance(category, int):
            return make_response(
                jsonify({
                    'message': "category cannot be number"
                })), 400
        if category and len(category.strip()) < 3:
            return make_response(
                jsonify({
                    'message': "category cannot be empty"
                })), 400
        if category and category.isdigit():
            return make_response(
                jsonify({
                    'message': 'Category cannot be Integer'
                })), 400
        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*',
                    str(category)):
            return make_response(
                jsonify({
                    'message':
                    "category should not have special characters"
                })), 400
        if location and isinstance(location, int):
            return make_response(
                jsonify({
                    'message': "location cannot be number"
                })), 400
        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*',
                    str(location)):
            return make_response(
                jsonify({
                    'message':
                    "location should not have special characters"
                })), 400
        if location and len(location.strip()) < 3:
            return make_response(
                jsonify({
                    'message': "location cannot be empty"
                })), 400
        if location and location.isdigit():
            return make_response(
                jsonify({
                    'message': 'Location cannot be Integer'
                })), 400
        event.name = name
        event.description = description
        event.category = category
        event.date_of_event = date_of_event
        event.location = location
        event.save_event()
        response = {
            'event': event.serialize(),
            'message': 'event updated successfully'
        }
        return make_response(jsonify(response)), 200

    @login_required
    def delete(self, user_id, id):
        """Delete an event according to the event id given."""
        events = Event.query.filter_by(author=user_id, id=id).first()
        if not events:
            return make_response(
                jsonify({
                    'message': 'event doesnt exist matching the id'
                })), 404
        events.delete_event()
        return make_response(jsonify({'message': 'event deleted'})), 200


class PublicEvent(MethodView):
    """Handles the public events ."""

    def get(self,id=None):
        """Enable the public to view the created events without authenication."""
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
            if q:
                events = Event.query.filter(Event.name.ilike("%" + q + "%"))
                result = [event.serialize() for event in events]
                return make_response(jsonify(result)), 200
            events = Event.query.paginate(int(page), int(limit), False)
            prev_page = ''
            next_page = ''
            pages = events.pages
            if events.has_prev:
                prev_page = '/public-events/?limit={}&page={}'.format(
                    limit, events.prev_num)
            if events.has_next:
                next_page = '/public-events/?limit={}&page={}'.format(
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
                return make_response(
                    jsonify({
                        'message': 'This event is not available'
                    })), 404
            response = event.serialize()
            return make_response(jsonify(response)), 200

event_blueprint.add_url_rule(
    '/create-event', view_func=Events.as_view('event'), methods=['POST'])
event_blueprint.add_url_rule(
    '/events', view_func=Events.as_view('events'), methods=['GET'])
event_blueprint.add_url_rule(
    '/events/<int:id>/',
    view_func=Events.as_view('view-events'),
    methods=['DELETE', 'PUT', 'GET'])
event_blueprint.add_url_rule(
    '/public-events',
    view_func=PublicEvent.as_view('public-events'),
    methods=['GET'])
event_blueprint.add_url_rule(
    '/public-events/<int:id>/',
    view_func=PublicEvent.as_view('public-event'),
    methods=['GET'])    
