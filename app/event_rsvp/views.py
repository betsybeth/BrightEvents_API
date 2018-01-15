from flask import Blueprint, request, jsonify, make_response
from flask.views import MethodView
import re
from app.models import Rsvp
from app.models import Event
from app.decorators.decorators import login_required

rsvp_blueprint = Blueprint('rsvp', __name__)


class Rsvps(MethodView):

    @login_required
    def post(self, id, user_id):
        event = Event.query.filter_by(id=id).first()
        if not event:
            response = {'message': 'No event available'}
            return make_response(jsonify(response)), 404
        json_dict = request.get_json()
        name = json_dict.get('name')
        email = json_dict.get('email')
        phone_no = json_dict.get('phone_no')
        category = json_dict.get('category')

        if not isinstance(name, str) or not name.isalpha():
            return make_response(
                jsonify({'message': 'Name cannot be Integer or empty'})), 400
        if name and name.strip():
            rsvp = Rsvp.query.filter_by(event_id=id, name=name).first()
            if rsvp:
                return make_response(
                    jsonify({'message': 'Rsvp already exists'})), 409
            if not re.match(r"([\w\.-]+)@([\w\.-]+)(\.[\w\.]+$)", email):
                return make_response(
                    jsonify({'message': 'Invalid email'})), 400
            if phone_no.strip() == " ":
                return make_response(
                    jsonify({'message': 'Invalid phone_no'})), 400
            if len(phone_no) < 9:
                return make_response(
                    jsonify({'message': 'phone_no too short'})), 400
            if not isinstance(category, str):
                return make_response(
                    jsonify({'message': 'Category cannot be Integer or empty'})), 400
            rsvp = Rsvp(
                name=name,
                email=email,
                phone_no=phone_no,
                category=category,
                event_id=id
            )
            rsvp.save_rsvp()
            response = {
                'name': rsvp.name,
                "email": rsvp.email,
                'phone_no': rsvp.phone_no,
                'category': rsvp.category,
                'event_id': rsvp.event_id,
                'id': rsvp.id,
                'message': 'rsvp successfully created'
            }
            return make_response(jsonify(response)), 201

    @login_required
    def get(self, user_id, id, _id=None):

        if _id is None:
            try:
                limit = request.headers.get('limit', default=20, type=int)
                page = request.headers.get('page', default=1, type=int)
            except TypeError as e:
                return make_response(
                    jsonify({"error": "limit and page must be int"})), 400
            if int(limit) > 6:
                limit = 6
            else:
                limit = int(limit)
            q = request.args.get('q', type=str)
            if q:
                event = Event.query.filter_by(author=user_id, id=id).first()
                if not event:
                    response = {
                        'message': 'Event is not available'
                    }
                    return make_response(jsonify(response)), 404
                rsvps_found = Rsvp.query.filter_by(
                    event_id=id).filter(
                    Rsvp.name.ilike(q))
                results = []
                for rsvp in rsvps_found:
                    rsvp_search = {
                        'name': rsvp.name,
                        "email": rsvp.email,
                        'phone_no': rsvp.phone_no,
                        'category': rsvp.category,
                        'event_id': rsvp.event_id,
                        'id': rsvp.id
                    }
                    results.append(rsvp_search)
                return make_response(jsonify(results=results)), 200
            elif q:
                event = Event.query.filter_by(author=user_id, id=id).first()
                if not event:
                    response = {
                        'message': 'Event is not available'
                    }
                    return make_response(jsonify(response)), 404
                rsvps_found = Rsvp.query.filter_by(
                    event_id=id).filter(
                    Rsvp.category.ilike(q))
                results = []
                for rsvp in rsvps_found:
                    rsvp_search = {
                        'name': rsvp.name,
                        "email": rsvp.email,
                        'phone_no': rsvp.phone_no,
                        'category': rsvp.category,
                        'event_id': rsvp.event_id,
                        'id': rsvp.id
                    }
                    results.append(rsvp_search)
                return make_response(jsonify(results=results)), 200
            else:
                event = Event.query.filter_by(author=user_id, id=id).first()
                if not event:
                    response = {
                        'message': 'Event is not available'
                    }
                    return make_response(jsonify(response)), 404
                rsvps = Rsvp.query.filter_by(
                    event_id=id).paginate(
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
                return make_response(jsonify(results=results, prev_page=prev_page,
                                             next_page=next_page,
                                             pages=pages)), 200

        else:
            rsvps = Rsvp.query.filter_by(id=_id).first()
            if not rsvps:
                response = {
                    'message': 'Rsvp is not available'
                }
                return make_response(jsonify(response)), 404
            response = rsvps.serialize()
            return make_response(jsonify(response)), 200

    @login_required
    def put(self, user_id, id, _id):
        rsvp = Rsvp.query.filter_by(event_id=id, id=_id).first()
        json_dict = request.get_json()
        name = json_dict.get('name')
        email = json_dict.get('email')
        phone_no = json_dict.get('phone_no')
        category = json_dict.get('category')
        if not rsvp:
            response = {
                'message': 'no rsvp available'
            }
            return make_response(jsonify(response)), 404
        if name.strip == "" or not isinstance(name, str):
            return make_response(jsonify({'message': 'Invalid name'})), 400
        if not re.match(r"([\w\.-]+)@([\w\.-]+)(\.[\w\.]+$)", email):
            return make_response(jsonify({'message': 'Invalid email'})), 400
        if phone_no.strip() == "":
            return make_response(jsonify({'message': 'Invalid phone_no'})), 400
        if len(phone_no) < 9:
            return make_response(
                jsonify({'message': 'phone_no too short'})), 400
        rsvp.name = name
        rsvp.email = email
        rsvp.phone_no = phone_no
        rsvp.category = category
        rsvp.save_rsvp()
        response = rsvp.serialize()
        return make_response(jsonify(response)), 200

    @login_required
    def delete(self, user_id, id, _id):
        rsvp = Rsvp.query.filter_by(event_id=id, id=_id).first()
        if not rsvp:
            response = {
                'message': 'Rsvp does not exist'
            }
            return make_response(jsonify(response)), 404
        rsvp.delete_rsvp()
        response = {
            'message': 'Rsvp deleted successfully'
        }
        return make_response(jsonify(response)), 200


rsvp_blueprint.add_url_rule(
    '/events/<id>/create_rsvp/',
    view_func=Rsvps.as_view('create_rsvp'),
    methods=['POST'])
rsvp_blueprint.add_url_rule(
    '/events/<id>/rsvps/', view_func=Rsvps.as_view('rsvps'), methods=['GET'])
rsvp_blueprint.add_url_rule(
    '/events/<int:id>/rsvps/<int:_id>/',
    view_func=Rsvps.as_view('view_rsvps'),
    methods=[
        'DELETE',
        'PUT',
        'GET'])
