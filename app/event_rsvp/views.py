import re
from flask import Blueprint, request, jsonify, make_response
from flask.views import MethodView
from app.models import Rsvp
from app.models import Event
from app.decorators.decorators import login_required

rsvp_blueprint = Blueprint('rsvp', __name__)


class Rsvps(MethodView):
    "class handles rsvps of an event."

    @login_required
    def post(self, id, user_id):
        """A user is able to create an rsvp\
         of an event according to the event Id."""
        event = Event.query.filter_by(author=user_id, id=id).first()
        if not event:
            return make_response(
                jsonify({'message': 'This event is not available'})), 404
        json_dict = request.get_json()
        email = json_dict.get('email')
        if not re.match(r"([\w\.-]+)@([\w\.-]+)(\.[\w\.]+$)", str(email)):
            return make_response(jsonify({'message': 'invalid email'})), 400
        rsvp = Rsvp.query.filter_by(event_id=id, email=email).first()
        if rsvp:
            return make_response(
                jsonify({'message': "Rsvp already exists"})), 409
        rsvp = Rsvp(
            email=email,
            event_id=id)
        rsvp.save_rsvp()
        response = {
            "email": rsvp.email,
            'event_id': rsvp.event_id,
            'id': rsvp.id,
            'message': 'rsvp successfully created'
        }
        return make_response(jsonify(response)), 201

    @login_required
    def get(self, user_id, id, _id=None):
        """Gets all the created rsvp and \
        also gets an rsvp according to it Id."""
        if _id is None:
            try:
                limit = request.headers.get('limit', default=20, type=int)
                page = request.headers.get('page', default=1, type=int)
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
                event = Event.query.filter_by(author=user_id, id=id).first()
                if not event:
                    return make_response(
                        jsonify({'message':
                                 'This event is not available'})), 404
                rsvps_found = Rsvp.query.filter_by(event_id=id).filter(
                    Rsvp.name.ilike("%" + q + "%"))
                results = []
                for rsvp in rsvps_found:
                    rsvp_search = {
                        "email": rsvp.email,
                        'event_id': rsvp.event_id,
                        'id': rsvp.id
                    }
                    results.append(rsvp_search)
                return make_response(jsonify(results=results)), 200

            else:
                event = Event.query.filter_by(author=user_id, id=id).first()
                if not event:
                    return make_response(
                        jsonify({'message':
                                 'This event is not available'})), 404
                rsvps = Rsvp.query.filter_by(event_id=id).paginate(
                    int(page), int(limit), False)
                prev_page = ''
                next_page = ''
                pages = rsvps.pages
                if rsvps.has_prev:
                    prev_page = '/events/{}/rsvps/?limit={}&page={}'.format(
                        id, limit, rsvps.prev_num)
                if rsvps.has_next:
                    next_page = '/events/{}/rsvps/?limit={}&page={}'.format(
                        id, limit, rsvps.next_num)
                results = []
                results = [rsvp.serialize() for rsvp in rsvps.items]
                return make_response(
                    jsonify(
                        results=results,
                        prev_page=prev_page,
                        next_page=next_page,
                        pages=pages)), 200

        else:
            rsvps = Rsvp.query.filter_by(id=_id).first()
            if not rsvps:
                return make_response(
                    jsonify({'message': 'Rsvp is not available'})), 404
            response = rsvps.serialize()
            return make_response(jsonify(response)), 200

    @login_required
    def put(self, user_id, id, _id):
        """Edits an Rsvp."""
        rsvp = Rsvp.query.filter_by(event_id=id, id=_id).first()
        json_dict = request.get_json()
        email = json_dict.get('email')
        if not rsvp:
            return make_response(
                jsonify({'message': 'this rsvp is not available'})), 404
        if not re.match(r"([\w\.-]+)@([\w\.-]+)(\.[\w\.]+$)", str(email)):
            return make_response(jsonify({'message': 'Invalid email'})), 400
        rsvp.email = email
        rsvp.save_rsvp()
        response = rsvp.serialize()
        return make_response(jsonify(response)), 200

    @login_required
    def delete(self, user_id, id, _id):
        """Deletes an Rsvp according to the rsvp Id."""
        rsvp = Rsvp.query.filter_by(event_id=id, id=_id).first()
        if not rsvp:
            return make_response(
                jsonify({'message': 'this rsvp does not exist'})), 404
        rsvp.delete_rsvp()
        response = {'message': 'Rsvp deleted successfully'}
        return make_response(jsonify(response)), 200


class PublicRsvp(MethodView):
    """Handles the public rsvps."""

    @staticmethod
    def post(id):
        """Enables anyone to rsvp to any event without authenication."""
        event = Event.query.filter_by(id=id).first()
        if not event:
            response = {'message': 'No event available'}
            return make_response(jsonify(response)), 404
        json_dict = request.get_json()
        email = json_dict.get('email')
        if not re.match(r"([\w\.-]+)@([\w\.-]+)(\.[\w\.]+$)", str(email)):
            return make_response(jsonify({'message': 'invalid email'})), 400
        rsvp = Rsvp(
            email=email,
            event_id=id)
        rsvp.save_rsvp()
        response = {
            "email": rsvp.email,  
            "message":"You rsvp'd to {} ".format(event.name)  
        }
        return make_response(jsonify(response)), 201

    @login_required
    def get(self, user_id ,id):
        """Enable the public to view the\
         created rsvp without authenication."""
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
            event = Event.query.filter_by(author=user_id,id=id).first()
            if not event:
                return make_response(jsonify({'message':
                                              'Event is not available'})), 404
            rsvps_found = Rsvp.query.filter_by(event_id=id).filter(
                Rsvp.name.ilike("%" + q + "%"))
            results = []
            for rsvp in rsvps_found:
                rsvp_search = {         
                    "email": rsvp.email,
                    'event_id': rsvp.event_id
                }
                results.append(rsvp_search)
            return make_response(jsonify(results=results)), 200
        else:
            event = Event.query.filter_by(author=user_id, id=id).first()
            if not event:
                return make_response(
                    jsonify({'message':
                             'Event is not available'})), 404
            rsvps = Rsvp.query.filter_by(event_id=id).paginate(
                int(page), int(limit), False)
            prev_page = ''
            next_page = ''
            pages = rsvps.pages
            if rsvps.has_prev:
                prev_page = '/events/{}/rsvps/?limit={}&page={}'.format(
                    id, limit, rsvps.prev_num)
            if rsvps.has_next:
                next_page = '/events/{}/rsvps/?limit={}&page={}'.format(
                    id, limit, rsvps.next_num)
            results = []
            results = [rsvp.serialize() for rsvp in rsvps.items]
            return make_response(
                jsonify(
                    results=results,
                    prev_page=prev_page,
                    next_page=next_page,
                    pages=pages)), 200


rsvp_blueprint.add_url_rule(
    '/events/<id>/create-rsvp/',
    view_func=Rsvps.as_view('create_rsvp'),
    methods=['POST'])
rsvp_blueprint.add_url_rule(
    '/events/<id>/rsvps/', view_func=Rsvps.as_view('rsvps'), methods=['GET'])
rsvp_blueprint.add_url_rule(
    '/events/<int:id>/rsvps/<int:_id>/',
    view_func=Rsvps.as_view('view_rsvps'),
    methods=['DELETE', 'PUT', 'GET'])
rsvp_blueprint.add_url_rule(
    '/public-events/<int:id>/public-rsvps',
    view_func=PublicRsvp.as_view('public_rsvps'),
    methods=['POST', "GET"])
