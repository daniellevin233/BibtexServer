import os
import re
import subprocess
import platform
import sqlite3
import json
import enum
from base64 import b64encode

#  csl file containing specification of citation rules to be applied
CITATION_STYLE_FILE = 'apa.csl'

#  temporary md file for holding citation generated by pandoc
TMP_CITATION_FILE = 'tmp_citation.md'

#  configuration file - specifies the bibtex database path and citation base rule
CONFIGURATIONS = 'bib_config.md'

TABLE_NAME = 'bibliography'

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

def get_bibtex_str(bibtex_dict):
    '''
    :param: bibtex_dict: Dictionary - BIBTEX record, must contain 'key' and 'entry_type' keys.
    :return: A single bibtex record string
    '''
    bibtex_lines = ['@{0} {{{1}'.format(bibtex_dict['entry_type'].upper(), bibtex_dict['key'])]
    for key, value in bibtex_dict.items():
        if key != 'entry_type' and key != 'key':  # @article{Sh:155,
            bibtex_lines.append('\t{0} = {{{1}}}'.format(key, value))
    return ',\n'.join(bibtex_lines) + '\n}'

def get_citation(bibtex_dict):
    '''
    :param bibtex_dict:  "entry_type": "Article",
                         "key": "author2020",
                         "title": "Egyptology",
                         "author": "Author",
                         "year": "2020",
                         ...
    :return: Creates citation based on given bibtex dictionary: "Author. (2020). *Egyptology*."
    '''

    #  fetch the name of the temporal file that will be looked up for extracting bibtex entries
    with open(CONFIGURATIONS, 'r') as config_file:
        try:
            r = re.compile(r"bibliography: ?'(.+)'")
            tmp_bib_database_file = r.search(config_file.read()).group(1)
        except AttributeError:
            raise Exception('Configuration file is not valid')

    #  generating the temporal bibtex database for containing necessary bibtex entries
    with open(tmp_bib_database_file, 'w+') as bibfile:
        bibfile.write(get_bibtex_str(bibtex_dict))

    #  generating the .md file with citation

    #  generating a .md file (CITATION_FILE) with citations for every entry of the .bib database mentioned in
    #  CONFIGURATIONS file
    subprocess.run('pandoc -t markdown_strict --csl={0} --filter=pandoc-citeproc --standalone {1} -o {2}'.
                   format(CITATION_STYLE_FILE, CONFIGURATIONS, TMP_CITATION_FILE), capture_output=True)

    #  extracting the citation from the generated .md file
    read_file_command = 'cat'
    if platform.system() == 'Windows':
        read_file_command = 'type'
    citation = subprocess.run('{0} {1}'.format(read_file_command, TMP_CITATION_FILE), shell=True, capture_output=True)

    #  deleting tmp files

    os.remove(tmp_bib_database_file)
    os.remove(TMP_CITATION_FILE)

    return citation.stdout.decode('utf-8').splitlines()[0]

def add_biblio_item(POST_data, conn, c):
    '''
    Adds single biblio record to the table bibliography
    :param POST_data: must contain the fields:  bibtex_json (TEXT),
                                                added_by (INTEGER),
                                                abbreviation (TEXT)
    '''
    try:
        abbr = None
        if 'abbreviation' in POST_data:
            abbr = POST_data['abbreviation']
        c.execute(
            """INSERT INTO {0} (
                  abbreviation,
                  description,
                  added_by
                  )
               VALUES (?,?,?)""".format(TABLE_NAME), (abbr,
                                                       POST_data['bibtex_json'],
                                                       POST_data['added_by'])
            )
        new_id = c.lastrowid
        conn.commit()
        return str(new_id)
    except sqlite3.Error as e:
        conn.rollback()
        raise e

def get_all_records_as_dict(c):
    results = {}
    row_items = c.execute('SELECT * FROM {0};'.format(TABLE_NAME))
    for record in row_items:
        results[record[0]] = {
            "abbreviation": record[1],
            "title": get_citation(json.loads(record[2]))
        }
    return results

def get_all_bibtex_as_dict(c):
    results = {}
    row_items = c.execute('SELECT * FROM {0};'.format(TABLE_NAME))
    for record in row_items:
        results[record[0]] = {
            "abbreviation" : record[1],
            "bibtex": str(b64encode(bytes(get_bibtex_str(json.loads(record[2])), 'utf8')))
        }
    return results

def get_record_by_id(c, id):
    record_dic = None
    c.execute('SELECT * FROM {0} WHERE id = (?)'.format(TABLE_NAME), (id,))
    record = c.fetchone()
    if record:
        record_dic = {
            "bibtex": record[2],
            "abbreviation": record[1]
        }
    return record_dic

def get_bibtex_by_id(c, id):
    bibtex_str = None
    c.execute('SELECT * FROM {0} WHERE id = (?)'.format(TABLE_NAME), (id,))
    record = c.fetchone()
    if record:
        bibtex_str = record[2]
    return bibtex_str

def update_biblio_item(id, PUT_data, conn, c):
    """
    Updates (PUT) single biblio record in the table bibliography
    :param PUT_data: must contain the fields:  bibtex_json (TEXT),
                                                added_by (INTEGER),
                                                abbreviation (TEXT)
    :param id: the id of the entry that's desired to be updated
    """
    try:
        c.execute(
            """UPDATE {0} 
               SET abbreviation = ?, 
                   description = ?,
                   added_by = ?
               WHERE id = ?;""".format(TABLE_NAME), (PUT_data['abbreviation'],
                                                     PUT_data['bibtex_json'],
                                                     PUT_data['added_by'],
                                                     id))
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise e

def delete_biblio_item(id, conn, c):
    try:
        c.execute(
            """DELETE FROM {0}
               WHERE id = ?;""".format(TABLE_NAME), (id, )
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise e

def get_biggest_id():
    """
    :return: the biggest ID in the database so far
    """
    global c
    try:
        conn = sqlite3.connect(f'../data/biblio.db')
        c = conn.cursor()
        c.execute(
            """SELECT max(id) FROM {0};""".format(TABLE_NAME)
        )
        res = c.fetchone()
        if not res:
            raise Exception("The table sqlite_sequence doesn't contain tuple for '{0}' table".format(TABLE_NAME))
        return res[0]
    except sqlite3.Error as e:
        print(f'Exception occured when accessing the database: {e}')
    finally:
        c.close()
