from flask import Flask, request, make_response, jsonify
from flask_restplus import Api, Resource, fields
from BiblioProcessing import *

POST_ACTIONS = ['add']

GET_ACTIONS = [
    'all',
    'allbibtex',
    'recordbyid',
    'bibtexbyid'
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
api = Api(app=app)
name_space = api.namespace('bibliography', description='Bibliography API')

class NullableString(fields.String): # TODO
    __schema_type__ = ['string', 'null']
    __schema_example__ = 'nullable string'

model = api.model('Test Model',
		            {'abbreviation': NullableString(required=False,
                                                    description="Abbreviation of the record"), #  TODO
                     'bibtex_json': fields.String(required=True,
                                                    description=BIBTEX_JSON_DESCRIPTION),
                     'added_by': fields.Integer(required=True,
                                                    description="ID of the user")})

@name_space.route("/add")
class BibliographyPostClass(Resource):

    @api.expect(model, validate=True)
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

@name_space.route("/updatebyid/<int:id>")
class BibliographyGetBibtexByIdClass(Resource):

    @api.expect(model, validate=True)
    def put(self, id):
        return request_handler('update', request, id)

@name_space.route("/deletebyid/<int:id>")
class BibliographyGetRecordByIdClass(Resource):

    def delete(self, id):
        return request_handler('delete', request, id)


def request_handler(action, request=None, id=None):
    '''

    :param action:
    :return:
    '''
    global c
    resp, conn = None, None
    try:
        conn = sqlite3.connect(f'../data/biblio.db')
        c = conn.cursor()

        if action not in (GET_ACTIONS + POST_ACTIONS + PUT_ACTIONS + DELETE_ACTIONS):
            resp = make_response('This action is not available', 400)
        elif (action in GET_ACTIONS and request.method != 'GET') or \
                (action in POST_ACTIONS and request.method != 'POST') or \
                (action in PUT_ACTIONS and request.method != 'PUT') or \
                (action in DELETE_ACTIONS and request.method != 'DELETE'):
            resp = make_response(f'Wrong request method "{request.method}" for action "{action}"', 400)
        elif (action == 'all'):
            resp = make_response(jsonify(get_all_records_as_dict(c)), 200)
        elif (action == 'add'):
            POST_data = json.loads(request.data)
            new_id = add_biblio_item(POST_data, conn, c)
            resp = make_response(new_id, 200)
        elif (action == 'allbibtex'):
            resp = make_response(jsonify(get_all_bibtex_as_dict(c)), 200)
        elif (action == 'recordbyid'):
            if type(id) is not int:
                resp = make_response('No id given or wrong format', 400)
            else:
                bibtex_str = get_record_by_id(c, id)
                if not bibtex_str:
                    resp = make_response('Record with given id not found', 404)
                else:
                    resp = make_response(jsonify(bibtex_str), 200)
        elif (action == 'bibtexbyid'):
            if type(id) is not int:
                resp = make_response('No id given or wrong format', 400)
            else:
                bibtex_str = get_bibtex_by_id(c, id)
                if not bibtex_str:
                    resp = make_response('Bibtex with given id not found', 404)
                else:
                    resp = make_response(bibtex_str, 200)
        elif (action == 'update'):
            c.execute('SELECT * FROM bibliography WHERE id = (?)', (id,))
            record = c.fetchone()
            if record is None:
                resp = make_response(f'Bibliography entry with id {id} not found to update', 404)
            else:
                PUT_DATA = json.loads(request.data)
                update_biblio_item(id, PUT_DATA, conn, c)
                resp = make_response(str(id), 200)
        elif (action == 'delete'):
            c.execute('SELECT * FROM bibliography WHERE id = (?)', (id, ))
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
    finally:
        c.close()