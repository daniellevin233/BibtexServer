import sqlite3
import json
import requests

from flask import Flask, request, make_response, jsonify, send_file
from BiblioProcessing import *

GET_ACTIONS = [
    'all',
    'allbibtex',
    'recordbyid',
    'bibtexbyid'
]

POST_ACTIONS = ['add']

app = Flask(__name__)
# AUTH_SERVER_URL = 'https://iclassifier.pw/api/authserver' #  TODO ?

@app.route('/<action>', methods=['POST', 'GET'])
def request_handler(action):
    '''

    :param action:
    :return:
    '''
    conn = sqlite3.connect(f'../data/biblio.db')
    c = conn.cursor()

    if action not in (GET_ACTIONS + POST_ACTIONS):  # TODO - necessary check?
        resp = make_response('This action is not available', 400) # any another steps to be done here?
        return resp
    elif (action in GET_ACTIONS and request.method == 'POST') or \
            (action in POST_ACTIONS and request.method == 'GET'):  # needed to be checked?
        resp = make_response(f'Wrong request method "{request.method}" for action "{action}"', 400)
        return resp
    elif (action == 'all'):
        resp =  make_response(, 200)



# if __name__ == '__main__':
#     print(BibtexEntryTypes.Article)
