import os
import re
import subprocess
import sqlite3
import json
from base64 import b64encode

# csl file containing specification of citation rules to be applied
# the content of the <sort> tag must be empty
CITATION_STYLE_FILE = 'chicago-author-date.csl' # 'apa.csl'

#  configuration file - specifies the .bib bibliography path and citation base rule
CONFIGURATIONS_BIBTEX = 'bib_config.md'

TABLE_NAME = 'bibliography'

def get_bibtex_str(bibtex_dict):
    '''
    :param: bibtex_dict: Dictionary - BIBTEX record, must contain 'key' and 'entry_type' keys.
    :return: A single bibtex record as a string
    '''
    bibtex_lines = ['@{0} {{{1}'.format(bibtex_dict['entry_type'].upper(), bibtex_dict['key'])]
    for key, value in bibtex_dict.items():
        if key != 'entry_type' and key != 'key':  # @article{Sh:155,
            bibtex_lines.append('\t{0} = {{{1}}}'.format(key, value))
    return ',\n'.join(bibtex_lines) + '\n}'

def get_citations():
    '''
    Generates citations for bibtex records stored in the bibtex database that is specified in CONFIGURATIONS_BIBTEX file
    :return: list of strings (citations)
    '''

    # configure a command that will generate a citation according to the .csl file specified in CITATION_STYLE_FILE
    command = 'pandoc -t markdown_strict --csl={0} --filter=pandoc-citeproc --standalone {1}'. \
            format(CITATION_STYLE_FILE, CONFIGURATIONS_BIBTEX)

    # generating the citations
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE)

    # extracting the citations from stdout and splitting them into list of citations
    blank_line_regex = r'(?:\r?\n){2,}'
    # with open('citations.txt', 'w') as f: # todo clean
    #     f.write(process.stdout.decode('utf-8').strip())
    # extract citations separated by blank line
    citations = re.split(blank_line_regex, process.stdout.decode('utf-8').strip())

    # replace remaining new line characters by whitespaces
    citations = list(map(lambda x: re.sub(r'(?:\r?\n)', ' ', x), citations))

    return citations

def get_bib_db_name():
    """
    Fetch the name of the temporal file that will be used for extracting bibtex entries
    """
    with open(CONFIGURATIONS_BIBTEX, 'r') as config_file:
        try:
            r = re.compile(r"bibliography: ?'(.+)'")
            tmp_bib_database_file = r.search(config_file.read()).group(1)
        except AttributeError:
            raise Exception('Bibtex configuration file is not valid')
    return tmp_bib_database_file

def add_biblio_item(POST_data, conn, c):
    '''
    Adds single biblio record to the table bibliography
    :param POST_data: must contain the fields:  bibtex_json (TEXT),
                                                added_by (INTEGER),
                                                abbreviation (TEXT),
                                                project_type (TEXT)
    '''
    try:
        abbr = None
        if 'abbreviation' in POST_data:
            abbr = POST_data['abbreviation']
        c.execute(
            """INSERT INTO {0} (
                  abbreviation,
                  description,
                  added_by,
                  project_type)
               VALUES (?,?,?,?)""".format(TABLE_NAME), (abbr,
                                                        POST_data['bibtex_json'],
                                                        POST_data['added_by'],
                                                        POST_data['project_type'])
            )
        new_id = c.lastrowid
        conn.commit()
        return new_id
    except sqlite3.Error as e:
        conn.rollback()
        raise e

def get_all_records_as_dict(c):
    results = {}
    c.execute('SELECT id, abbreviation, description FROM {0};'.format(TABLE_NAME))
    row_items = c.fetchall()
    tmp_bib_database_file_path = get_bib_db_name()

    #  generating and populating the temporal bibtex database for storing bibtex entries
    with open(tmp_bib_database_file_path, 'a') as bibfile:
        for record in row_items:
            bibfile.write(get_bibtex_str(json.loads(record[2])) + '\n')

    # extracting the list of citations
    citations = get_citations()

    # generating the output
    for citation, record in zip(citations, row_items):
        results[record[0]] = {
            "abbreviation": record[1],
            "title": citation
        }

    # cleaning the temporal bibtex database
    os.remove(tmp_bib_database_file_path)

    return results

def get_all_bibtex_as_dict(c):
    results = {}
    row_items = c.execute('SELECT id, abbreviation, description FROM {0};'.format(TABLE_NAME))
    for record in row_items:
        results[record[0]] = {
            "abbreviation" : record[1],
            "bibtex": str(b64encode(bytes(get_bibtex_str(json.loads(record[2])), 'utf8')))
        }
    return results

def get_record_by_id(c, id):
    record_dic = None
    c.execute('SELECT abbreviation, description FROM {0} WHERE id = (?)'.format(TABLE_NAME), (id,))
    record = c.fetchone()
    if record:
        record_dic = {
            "bibtex": record[1],
            "abbreviation": record[0]
        }
    return record_dic

def get_bibtex_by_id(c, id):
    bibtex_str = None
    c.execute('SELECT description FROM {0} WHERE id = (?)'.format(TABLE_NAME), (id,))
    record = c.fetchone()
    if record:
        bibtex_str = record[0]
    return bibtex_str

def get_bibtex_json_by_id(c, id):
    bibtex_json = None
    c.execute('SELECT description FROM {0} WHERE id = (?)'.format(TABLE_NAME), (id,))
    record = c.fetchone()
    if record:
        bibtex_json = json.loads(record[0])
    return bibtex_json

def update_biblio_item(id, PUT_data, conn, c):
    """
    Updates (PUT) single biblio record in the table bibliography
    :param PUT_data: must contain the fields:  bibtex_json (TEXT),
                                               added_by (INTEGER),
                                               abbreviation (TEXT)
                                               project_type (TEXT)
    :param id: the id of the entry to be updated
    """
    try:
        c.execute(
            """UPDATE {0} 
               SET abbreviation = ?, 
                   description = ?,
                   added_by = ?,
                   project_type = ?
               WHERE id = ?;""".format(TABLE_NAME), (PUT_data['abbreviation'],
                                                     PUT_data['bibtex_json'],
                                                     PUT_data['added_by'],
                                                     PUT_data['project_type'],
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

def get_next_id(conn, c):
    try:
        c.execute(
            """SELECT seq FROM sqlite_sequence 
               WHERE name = '{0}';""".format(TABLE_NAME)
        )
        res = c.fetchone()
        if not res:
            raise Exception("The table sqlite_sequence doesn't contain tuple for '{0}' table".format(TABLE_NAME))
        return res[0]
    except sqlite3.Error as e:
        conn.rollback()
        raise e