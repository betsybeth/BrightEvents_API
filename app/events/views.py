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
        event = Event(
            name=name,
            description=description,
            category=category,
            date=date,
            author=user_id,
            location=location)
        event.save_event()
        response = {
            'name': event.name,
            'description': event.description,
            'category': event.category,
            'date': event.date,
            'author': event.author,
            'location': event.location,
            'message': 'event successfully created'
        }
        return make_response(jsonify(response)), 201

    @login_required
    def get(self, user_id, _id=None):
        """Gets the created events."""
        events = Event.query.filter_by(author=user_id).first()
        if not _id:
            try:
                max_per_page = int(requests.args.get('max_per_page'))
                page = int(request.args.get('page'))
            except Exception as e:
                max_per_page = 6
                page = 1
            events = Event.query.filter_by(author=user_id).paginate(int(page), int(max_per_page), False)
            if events.has_prev:
                prev_page='/events,?max_per_page={}&page={}'.format(max_per_page, events.prev_num)
            if events.has_next:
                next_page='/events/?max_per_page={}&page={}'.format(max_per_page, events.next_num)
            if not events:
                response = {'message': 'Event not available'}
                return make_response(jsonify(response)), 404
            results=[event.serialize() for event in events.items]
            return make_response(jsonify(results)), 200
    @login_required
    def put(self, id, user_id):
        """Edits the created the event."""
        event = Event.query.filter_by(author=user_id).first()
        json_dict = request.get_json()
        name = json_dict.get('name')
        description = json_dict.get('description')
        category = json_dict.get('category')
        date = json_dict.get('date')
        location = json_dict.get('location')
        if not event:
            response = {
                'message':'no bucketlist available'
            }
            return make_response(jsonify(response)), 400
        else:
            event.name =name
            event.description = description
            event.category  =  category
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
            response = {
                'message':'event doesnt exist matching the id'
            }
            return make_response(jsonify(response)), 404
        else:
            events.delete_event()
            response = {
                'message':'event deleted'
            }
            return make_response(jsonify(response)), 204





event_blueprint.add_url_rule(
    '/create_event', view_func=Events.as_view('event'), methods=['POST'])
event_blueprint.add_url_rule(
    '/events', view_func=Events.as_view('events'), methods=['GET'])
event_blueprint.add_url_rule('/events/<int:id>/', view_func=Events.as_view('view_events'), methods=['DELETE', 'PUT'])
