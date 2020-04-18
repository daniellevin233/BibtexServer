from flask import Flask, request, make_response, jsonify
from flask_restplus import Api, Resource, fields
from flask_cors import CORS, cross_origin  # TODO
from BiblioProcessing import *

POST_ACTIONS = ['add']

GET_ACTIONS = [
    'all',
    'allbibtex',
    'recordbyid',
    'bibtexbyid',
    'bibtexjsonbyid'
]

PUT_ACTIONS = ['update']

DELETE_ACTIONS = ['delete']

BIBTEX_JSON_DESCRIPTION = """{
								"entry_type": "Article",
								"key": "lastname2020",
								"author": "Lastname",
								"title": "Title",
								"journal": "Egyptology",
								"year": "2020",
								...
							}"""

app = Flask(__name__)
CORS(app)
api = Api(app=app)
name_space = api.namespace('bibliography', description='Bibliography API')

model = api.model('Test Model',
                  {'abbreviation': fields.String(required=False,
                                                  description="Abbreviation of the record"),  # TODO
                   'bibtex_json': fields.String(required=True,
                                                description=BIBTEX_JSON_DESCRIPTION),
                   'added_by': fields.Integer(required=True,
                                              description="ID of the user")})


@name_space.route("/add")
class BibliographyPostClass(Resource):

    @api.expect(model, validate=True)
    @cross_origin()
    def post(self):
        return request_handler('add', request)


@name_space.route("/all")
class BibliographyGetAllClass(Resource):

    @cross_origin()
    def get(self):
        return request_handler('all', request)


@name_space.route("/allbibtex")
class BibliographyGetAllBibtexClass(Resource):

    @cross_origin()
    def get(self):
        return request_handler('allbibtex', request)


@name_space.route("/recordbyid/<int:id>")
class BibliographyGetRecordByIdClass(Resource):

    @cross_origin()
    def get(self, id):
        return request_handler('recordbyid', request, id)


@name_space.route("/bibtexbyid/<int:id>")
class BibliographyGetBibtexByIdClass(Resource):

    @cross_origin()
    def get(self, id):
        return request_handler('bibtexbyid', request, id)


@name_space.route("/bibtexjsonbyid/<int:id>")
class BibliographyGetBibtexByIdClass(Resource):

    @cross_origin()
    def get(self, id):
        return request_handler('bibtexjsonbyid', request, id)


@name_space.route("/updatebyid/<int:id>")
class BibliographyGetBibtexByIdClass(Resource):

    @api.expect(model, validate=True)
    @cross_origin()
    def put(self, id):
        return request_handler('update', request, id)


@name_space.route("/deletebyid/<int:id>")
class BibliographyGetRecordByIdClass(Resource):

    @cross_origin()
    def delete(self, id):
        return request_handler('delete', request, id)

requested_headers = ['X-PINGOTHER',
                     'Accept',
                     'Accept-Encoding',
                     'Accept-Language',
                     'Cache-Control',
                     'Connection',
                     'Content-Length',
                     'Content-Type',
                     'Host',
                     'Origin',
                     'Pragma',
                     'Referer',
                     'Sec-Fetch-Dest',
                     'Sec-Fetch-Mode',
                     'Sec-Fetch-Site',
                     'User-Agent']

@name_space.route("/")
class BibliographyOptions(Resource):

    def options(self):
        resp = make_response('OK', 200)
        # resp.headers['Access-Control-Request-Method'] = 'POST' #, GET, PUT, DELETE, OPTIONS'
        # resp.headers['Access-Control-Allow-Origin'] = '*'
        # resp.headers['Access-Control-Allow-Headers'] = ', '.join(requested_headers)
        # resp.headers['Access-Control-Max-Age'] = 10
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Credentials"] = "true"
        resp.headers["Access-Control-Allow-Methods"] = "GET,DELETE,OPTIONS,POST,PUT"
        resp.headers["Access-Control-Allow-Headers"] = "Access-Control-Allow-Headers, Access-Control-Allow-Methods, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers"
        print(resp.headers)
        return resp


api.add_resource(BibliographyOptions, '/')


def request_handler(action, request=None, id=None):
    """

    :param action:
    :return:
    """
    global c
    try:
        conn = sqlite3.connect(f'../data/biblio.db')
        c = conn.cursor()

        if action not in (GET_ACTIONS + POST_ACTIONS + PUT_ACTIONS + DELETE_ACTIONS):
            resp = make_response(f'The action "{action}" is not available', 400)
        elif (action in GET_ACTIONS and request.method != 'GET') or \
                (action in POST_ACTIONS and request.method != 'POST') or \
                (action in PUT_ACTIONS and request.method != 'PUT') or \
                (action in DELETE_ACTIONS and request.method != 'DELETE'):
            resp = make_response(f'Wrong request method "{request.method}" for action "{action}"', 400)
        elif action == 'all':
            resp = make_response(jsonify(get_all_records_as_dict(c)), 200)
        elif action == 'add':
            post_data = json.loads(request.data)
            bibtex_dict = json.loads(post_data['bibtex_json'])
            if 'entry_type' not in bibtex_dict:
                resp = make_response('Bad request: bibtex_json must contain the field entry_type', 400)
            else:
                bibtex_dict['key'] = str(get_next_id(conn, c) + 1)
                post_data['bibtex_json'] = json.dumps(bibtex_dict)
                new_id = add_biblio_item(post_data, conn, c)
                resp = make_response(str(new_id), 200)
                # resp.headers.add("Access-Control-Allow-Origin", "*") todo
        elif action == 'allbibtex':
            resp = make_response(jsonify(get_all_bibtex_as_dict(c)), 200)
        elif action == 'recordbyid':
            if type(id) is not int:
                resp = make_response('Bad request: no id given or wrong format', 400)
            else:
                record_dict = get_record_by_id(c, id)
                if not record_dict:
                    resp = make_response('Record with given id not found', 404)
                else:
                    resp = make_response(jsonify(record_dict), 200)
        elif action == 'bibtexbyid':
            if type(id) is not int:
                resp = make_response('No id given or wrong format', 400)
            else:
                bibtex_str = get_bibtex_by_id(c, id)
                if not bibtex_str:
                    resp = make_response('Bibtex with given id not found', 404)
                else:
                    resp = make_response(bibtex_str, 200)
        elif action == 'bibtexjsonbyid':
            if type(id) is not int:
                resp = make_response('No id given or wrong format', 400)
            else:
                bibtex_json = get_bibtex_json_by_id(c, id)
                if not bibtex_json:
                    resp = make_response('Bibtex with given id not found', 404)
                else:
                    resp = make_response(bibtex_json, 200)
        elif action == 'update':
            c.execute('SELECT * FROM bibliography WHERE id = (?)', (id,))
            record = c.fetchone()
            if record is None:
                resp = make_response(f'Bibliography entry with id {id} not found to update', 404)
            else:
                put_data = json.loads(request.data)
                if 'entry_type' not in json.loads(put_data['bibtex_json']):
                    resp = make_response('Bad request: bibtex_json must contain fields entry_type, key and author', 400)
                else:
                    update_biblio_item(id, put_data, conn, c)
                    resp = make_response(str(id), 200)
        elif action == 'delete':
            c.execute('SELECT * FROM bibliography WHERE id = (?)', (id,))
            record = c.fetchone()
            if record is None:
                resp = make_response(f'Bibliography entry with id {id} not found to delete', 404)
            else:
                delete_biblio_item(id, conn, c)
                resp = make_response(str(id), 200)
        else:
            resp = None
        resp.headers['Access-Control-Allow-Origin'] = '*' # TODO
        return resp
    except sqlite3.Error as e:
        print(f'Exception occured when writing: {e}')
        return make_response(f'Internal server error: {e}', 500)
    finally:
        c.close()
