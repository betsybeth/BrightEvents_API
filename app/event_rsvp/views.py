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
        name = json_dict.get('name')
        email = json_dict.get('email')
        phone_no = json_dict.get('phone_no')
        category = json_dict.get('category')
        if name and isinstance(name, int):
            return make_response(
                jsonify({'message': "name cannot be number"})), 400
        if name and name.isdigit():
            return make_response(
                jsonify({'message': "name cannot be integer"})), 400
        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*', str(name)):
            return make_response(
                jsonify({'message':
                         "name should not have special characters"})), 400
        if not re.match(r"([\w\.-]+)@([\w\.-]+)(\.[\w\.]+$)", str(email)):
            return make_response(jsonify({'message': 'invalid email'})), 400
        rsvp = Rsvp.query.filter_by(event_id=id, email=email).first()
        if rsvp:
            return make_response(
                jsonify({'message': "Rsvp already exists"})), 409
        if len(name.strip()) < 3:
            return make_response(
                jsonify({'message': "name cannot be empty"})), 400
        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*', str(name)):
            return make_response(
                jsonify({'message':
                         "name should not have special characters"})), 400
        if phone_no and len(phone_no.strip()) < 3:
            return make_response(
                jsonify({'message': "phone_no cannot be empty"})), 400

        if len(phone_no) < 9:
            return make_response(jsonify({
                'message': 'phone_no too short'
            })), 400
        if category and isinstance(category, int):
            return make_response(
                jsonify({'message': "category cannot be number"})), 400

        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*', category):
            return make_response(jsonify({
                'message': "category should not have special characters"
            })), 400
        if category and len(category.strip()) < 3:
            return make_response(
                jsonify({'message': "category cannot be empty"})), 400
        if category.isdigit():
            return make_response(
                jsonify({
                    'message': 'Category cannot be Integer'
                })), 400
        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*', category):
            return make_response(jsonify({
                'message': "category should not have special characters"
            })), 400
        rsvp = Rsvp(
            name=name,
            email=email,
            phone_no=phone_no,
            category=category,
            event_id=id)
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
        name = json_dict.get('name')
        email = json_dict.get('email')
        phone_no = json_dict.get('phone_no')
        category = json_dict.get('category')
        if not rsvp:
            return make_response(
                jsonify({'message': 'this rsvp is not available'})), 404
        if name and isinstance(name, int):
            return make_response(
                jsonify({'message': "name cannot be number"})), 400
        if name and name.isdigit():
            return make_response(
                jsonify({'message': "name cannot be integer"})), 400
        if name and len(name.strip()) < 3:
            return make_response(
                jsonify({'message': "name cannot be empty"})), 400
        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*', str(name)):
            return make_response(
                jsonify({'message':
                         "Name should not have special characters"})), 400
        if not re.match(r"([\w\.-]+)@([\w\.-]+)(\.[\w\.]+$)", str(email)):
            return make_response(jsonify({'message': 'Invalid email'})), 400
        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*', phone_no):
            return make_response(jsonify({
                'message': "Phone_no should not have special characters"
            })), 400
        if len(phone_no.strip()) < 3:
            return make_response(
                jsonify({'message': "phone_no cannot be empty"})), 400
        if len(phone_no) < 9:
            return make_response(jsonify({
                'message': 'phone_no too short'
            })), 400
        if category and isinstance(category, int):
            return make_response(
                jsonify({'message': "category cannot be number"})), 400
        if len(category.strip()) < 3:
            return make_response(
                jsonify({'message': "category cannot be empty"})), 400
        if category.isdigit():
            return make_response(
                jsonify({
                    'message': 'Category cannot be Integer'
                })), 400
        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*', category):
            return make_response(jsonify({
                'message': "category should not have special characters"
            })), 400
        rsvp.name = name
        rsvp.email = email
        rsvp.phone_no = phone_no
        rsvp.category = category
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
        name = json_dict.get('name')
        email = json_dict.get('email')
        phone_no = json_dict.get('phone_no')
        category = json_dict.get('category')
        if name and isinstance(name, int):
            return make_response(
                jsonify({'message': "name cannot be number"})), 400
        if name and name.isdigit():
            return make_response(
                jsonify({'message': "name cannot be integer"})), 400
        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*', str(name)):
            return make_response(
                jsonify({'message':
                         "name should not have special characters"})), 400
        if not re.match(r"([\w\.-]+)@([\w\.-]+)(\.[\w\.]+$)", str(email)):
            return make_response(jsonify({'message': 'invalid email'})), 400
        rsvp = Rsvp.query.filter_by(email=email).first()
        if rsvp:
            return make_response(
                jsonify({'message': "Rsvp already exists"})), 409
        if len(name.strip()) < 3:
            return make_response(
                jsonify({'message': "name cannot be empty"})), 400
        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*', str(name)):
            return make_response(
                jsonify({
                    'message':
                    "name should not have special characters"})), 400
        if phone_no and len(phone_no.strip()) < 3:
            return make_response(
                jsonify({'message': "phone_no cannot be empty"})), 400
        if len(phone_no) < 9:
            return make_response(jsonify({
                'message': 'phone_no too short'
            })), 400
        if category and isinstance(category, int):
            return make_response(
                jsonify({'message': "category cannot be number"})), 400
        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*', category):
            return make_response(jsonify({
                'message': "category should not have special characters"
            })), 400
        if category and len(category.strip()) < 3:
            return make_response(
                jsonify({'message': "category cannot be empty"})), 400
        if category.isdigit():
            return make_response(
                jsonify({
                    'message': 'Category cannot be Integer'
                })), 400
        if re.match(r'.*[\%\$\^\*\@\!\?\(\)\:\;\&\'\"\{\}\[\]].*', category):
            return make_response(jsonify({
                'message': "category should not have special characters"
            })), 400
        rsvp = Rsvp(
            name=name,
            email=email,
            phone_no=phone_no,
            category=category,
            event_id=id)
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

    @staticmethod
    def get(id):
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
            event = Event.query.filter_by(id=id).first()
            if not event:
                return make_response(jsonify({'message':
                                              'Event is not available'})), 404
            rsvps_found = Rsvp.query.filter_by(event_id=id).filter(
                Rsvp.name.ilike("%" + q + "%"))
            results = []
            for rsvp in rsvps_found:
                rsvp_search = {
                    'name': rsvp.name,
                    "email": rsvp.email,
                    'phone_no': rsvp.phone_no,
                    'category': rsvp.category,
                    'event_id': rsvp.event_id
                }
                results.append(rsvp_search)
            return make_response(jsonify(results=results)), 200
        else:
            event = Event.query.filter_by(id=id).first()
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
    '/events/<id>/create_rsvp/',
    view_func=Rsvps.as_view('create_rsvp'),
    methods=['POST'])
rsvp_blueprint.add_url_rule(
    '/events/<id>/rsvps/', view_func=Rsvps.as_view('rsvps'), methods=['GET'])
rsvp_blueprint.add_url_rule(
    '/events/<int:id>/rsvps/<int:_id>/',
    view_func=Rsvps.as_view('view_rsvps'),
    methods=['DELETE', 'PUT', 'GET'])
rsvp_blueprint.add_url_rule(
    '/public_events/<id>/public_rsvps',
    view_func=PublicRsvp.as_view('public_rsvps'),
    methods=['POST', 'GET'])
