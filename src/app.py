from flask import Flask, request, make_response, jsonify
from flask_restplus import Api, Resource, fields
from flask_cors import CORS
from BiblioProcessing import *
import ast

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
                                                  description="Abbreviation of the record"),
                   'bibtex_json': fields.String(required=True,
                                                description=BIBTEX_JSON_DESCRIPTION),
                   'added_by': fields.Integer(required=True,
                                              description="ID of the user"),
                   'project_type': fields.String(required=True,
                                                description="Type of the project this record is associated with")})

@name_space.route("/add")
class BibliographyPostClass(Resource):

    @api.expect(model, validate=False)
    def post(self):
        return request_handler('add', request)


@name_space.route("/all")
class BibliographyGetAllClass(Resource):

    def get(self):
        return request_handler('all', request)


@name_space.route("/allbibtex")
class BibliographyGetAllBibtexClass(Resource):

    def get(self):
        return request_handler('allbibtex', request)


@name_space.route("/recordbyid/<int:id>")
class BibliographyGetRecordByIdClass(Resource):

    def get(self, id):
        return request_handler('recordbyid', request, id)


@name_space.route("/bibtexbyid/<int:id>")
class BibliographyGetBibtexByIdClass(Resource):

    def get(self, id):
        return request_handler('bibtexbyid', request, id)


@name_space.route("/bibtexjsonbyid/<int:id>")
class BibliographyGetBibtexByIdClass(Resource):

    def get(self, id):
        return request_handler('bibtexjsonbyid', request, id)


@name_space.route("/updatebyid/<int:id>")
class BibliographyGetBibtexByIdClass(Resource):

    @api.expect(model, validate=False)
    def put(self, id):
        return request_handler('update', request, id)


@name_space.route("/deletebyid/<int:id>")
class BibliographyGetRecordByIdClass(Resource):

    def delete(self, id):
        return request_handler('delete', request, id)


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
                resp = make_response('Bad request: no id given or wrong format', 400)
            else:
                bibtex_str = get_bibtex_by_id(c, id)
                if not bibtex_str:
                    resp = make_response('Bibtex with given id not found', 404)
                else:
                    resp = make_response(bibtex_str, 200)
        elif action == 'bibtexjsonbyid':
            if type(id) is not int:
                resp = make_response('Bad request: no id given or wrong format', 400)
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
                    resp = make_response('Bad request: bibtex_json must contain the field entry_type', 400)
                else:
                    # adding key field to avoid requiring it from the user
                    # key field is important for generating bibtex record (e.g. to generate citations)
                    add_key_dict = ast.literal_eval(put_data['bibtex_json']) # convert string to dict
                    add_key_dict['key'] = f'{id}' # add the 'key' field
                    put_data['bibtex_json'] = json.dumps(add_key_dict) # update the payload
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
        return resp
    except sqlite3.Error as e:
        print(f'Exception occured when writing: {e}')
        return make_response(f'Internal server error: {e}', 500)
    finally:
        c.close()
