import sqlite3
import json
import app as app
import enum

""" # a code for fetching rows with sqlite3 as dictionaries rather than as tuples
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

con = sqlite3.connect(":memory:")
con.row_factory = dict_factory
cur = con.cursor()
cur.execute("select 1 as a")
print cur.fetchone()["a"]
"""

class BibtexEntryTypes(enum.Enum):
   Article = "Article"
   Book = "Book"
   Booklet = "Booklet"
   Conference = "Conference"
   InBook = "InBook"
   InCollection = "InCollection"
   InProceedings = "InProceedings"
   MastersThesis = "MastersThesis"
   Misc = "Misc"
   PhdThesis = "PhdThesis"
   Proceedings = "Proceedings"
   Unpublished = "Unpublished"
   URL = "URL"

BIBTEX_STR_EXEMPLAR = '''
@ARTICLE {levin2020,
    author  = "Levin",
    title   = "Backend",
    journal = "Journal backend by Flask",
    year    = "2020",
    volume  = "1",
    number  = "12",
    month   = "jan"
}
'''  # TODO clean afterwards

BIBTEX_JSON_EXEMPLAR = '''
{ 
"entry_type":"Article",
"key":"levin2020", 
"title":"Backend",
"journal":"Journal backend by Flask",
"year":"2020",
"volume":"1",
"number":"12",
"month":"jan"
}
'''  # TODO clean afterwards

def get_bibtex_str(bibtex_dict):  # TODO or not TODO?
    '''
    :param: bibtex_dict: Dictionary - BIBTEX record, must contain 'key' and 'entry_type' keys.
    :return: A single bibtex record string
    '''
    bibtex_lines = ['@{0} {{{1}'.format(bibtex_dict['entry_type'].upper(), bibtex_dict['key'])]
    for key, value in bibtex_dict.items():
        if key != 'entry_type' and key != 'key':  # @article{Sh:155,
            bibtex_lines.append('\t{0} = "{1}"'.format(key, value))
    return ',\n'.join(bibtex_lines) + '\n}'  # TODO check produced month format


def get_citation(bibtex_dict):  # TODO
    '''
    :param bibtex_dict:  "entry_type": "Article",
                         "key": "levin2020",
                         "title": "bib_title",
                         "author": "Levin",
                         "year": "2020",
                         ...
    :return: Creates citation based on given bibtex dictionary
    '''
    return "... here goes a citation"


def add_biblio_item(POST_data, conn, c):
    '''
    Adds single biblio record to the table bibliography
    :param POST_data: must contain the fields:  bibtex_json (TEXT),
                                                added_by (INTEGER),
                                                abbreviation (TEXT)
    '''
    try:
        if 'abbreviation' not in POST_data:
            POST_data['abbreviation'] = 'NULL'
        c.execute(
            """INSERT INTO bibliography (
                  abbreviation,
                  description,
                  added_by
                  )
               VALUES (?,?,?)""", (POST_data['abbreviation'],
                                   POST_data['bibtex_json'],
                                   POST_data['added_by'])
            )
        new_id = c.lastrowid
        conn.commit()
        return str(new_id)
        # extract_biblio_table(c) # TODO figure out what it does
    except sqlite3.Error as e:
        conn.rollback()  # TODO ?
        raise e

def get_all_records_as_dict(c):
    results = {}
    row_items = c.execute(f'SELECT * FROM bibliography;')
    for record in row_items:
        results[record[0]] = {
            "abbreviation": record[1],
            "title": get_citation(json.loads(record[2]))
        }
    return results

def get_all_bibtex_as_dict(c):
    results = {}
    row_items = c.execute(f'SELECT * FROM bibliography;')
    for record in row_items:
        results[record[0]] = {
            "abbreviation" : record[1],
            "bibtex": get_bibtex_str(json.loads(record[2]))
        }
    return results

def get_record_by_id(c, id):
    record_dic = None
    c.execute('SELECT * FROM bibliography WHERE id = (?)', (id,))
    record = c.fetchone()
    if record:
        record_dic = {
            "bibtex": record[2],
            "abbreviation": record[1]
        }
    return record_dic

def get_bibtex_by_id(c, id):
    bibtex_str = None
    c.execute('SELECT * FROM bibliography WHERE id = (?)', (id,))
    record = c.fetchone()
    if record:
        bibtex_str = record[2]
    return bibtex_str