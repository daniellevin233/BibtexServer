import sqlite3
import json

from flask import Flask, request, make_response, jsonify
from flask_restplus import Api, Resource, fields
from BiblioProcessing import *

GET_ACTIONS = [
    'all',
    'allbibtex',
    'recordbyid',
    'bibtexbyid'
]

POST_ACTIONS = ['add']

BIBTEX_JSON_DESCRIPTION = """{
								"entry_type": "Article",
								"key": "lastname2020",
								"author": "Lastname",
								"title": "Title",
								"journal": "Egyptology",
								"year": "2020",
								...
							}"""

flask_app = Flask(__name__)
app = Api(app=flask_app)
name_space = app.namespace('bibliography', description='Bibliography API')

model = app.model('Test Model',
		            {'abbreviation': fields.String(required = False,
                                                    description="Abbreviation of the record"),
                     'bibtex_json': fields.String(required=True,
                                                    description=BIBTEX_JSON_DESCRIPTION),
                     'added_by': fields.Integer(required=True,
                                                    description="ID of the user")})

# AUTH_SERVER_URL = 'https://iclassifier.pw/api/authserver' #  TODO ?

@name_space.route("/")
class BibliographyAppClass(Resource):

    def get(self):
        return make_response("Hello world", 200)

    @app.expect(model, validate=True)
    def post(self):
        return request_handler('add', request)
        # conn, c = None, None
        # try:
        #     POST_data = json.loads(request.data)
        #     my_p(POST_data)
        #     conn = self.connect()
        #     c = conn.cursor()
        #     new_id = add_biblio_item(POST_data, conn, c)
        #     resp = make_response(new_id, 200)
        #     return resp
        # except sqlite3.Error as e:
        #     print(f'Exception occured when writing: {e}')
        # finally:
        #     self.disconnect(conn)


    def disconnect(self, conn):
        if (conn):
            conn.close()

    def connect(self):
        conn = None
        try:
            conn = sqlite3.connect(f'../data/biblio.db')
        except sqlite3.Error as e:
            print(f'Exception occured when writing: {e}')
        return conn

# @app.route('/')
# def hello_world():
#     return 'Hello world!'


# @app.route('/<action>', methods=['POST', 'GET'])
def request_handler(action, request=None):
    '''

    :param action:
    :return:
    '''
    try:
        conn = sqlite3.connect(f'../data/biblio.db')
        c = conn.cursor()

        if action not in (GET_ACTIONS + POST_ACTIONS):  # TODO - necessary check?
            resp = make_response('This action is not available', 400) # TODO any another steps to be done here?
        elif (action in GET_ACTIONS and request.method == 'POST') or \
                (action in POST_ACTIONS and request.method == 'GET'):  # TODO needed to be checked?
            resp = make_response(f'Wrong request method "{request.method}" for action "{action}"', 400)
        elif (action == 'all'):
            # resp = make_response(jsonify(get_all_records(c)), 200)
            resp = make_response("Hello from all", 200)
        elif (action == 'add'):
            my_p(request.data)
            POST_data = json.loads(request.data)
            new_id = add_biblio_item(POST_data, conn, c)
            resp = make_response(new_id, 200)
        else:
            resp = None
        c.close()
        return resp
    except sqlite3.Error as e:
        print(f'Exception occured when writing: {e}')
    finally:
        if(conn):
            conn.close()


def my_p(data):
    print('======\n', str(data), '\n======\n')