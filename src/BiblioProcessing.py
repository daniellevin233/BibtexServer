import json
import enum

class BibtexEntryTypes(enum.Enum):
   Article = "Article"
   Book = "Book"
   Booklet = "Booklet"
   Conference = "Conference"
   InBook = "InBook"
   InCollection = "InCollection"
   InProceedings = "InProceedings"
   Manual = "Manual"
   MastersThesis = "MastersThesis"
   Misc = "Misc"
   PhdThesis = "PhdThesis"
   Proceedings = "Proceedings"
   TechReport = "TechReport"
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
'''

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
'''


def get_bibtex_dict(bibtex_str):  # TODO or not TODO?
    '''
    :param bibtex_str: String - record BIBTEX in bibtex format.
    :return: A simple dict with BibTeX field-value pairs,
             for example `'author': 'Bird, R.B. and Armstrong, R.C. and Hassager, O.'` Each
             entry will always have the following dict keys (in addition to other BibTeX fields):
                * `ID` (BibTeX key)
                * `ENTRYTYPE` (entry type in lowercase, e.g. `book`, `article` etc.)
    '''
    res = dict()
    return res


def get_bibtex_str(bibtex_dict):  # TODO or not TODO?
    '''
    :param: bibtex_dict: Dictionary - BIBTEX record.
    :return: A single bibtex record string
    '''
    bibtex_lines = ['@{0} {{{1}'.format(bibtex_dict['entry_type'].upper(), bibtex_dict['key'])]
    for key, value in bibtex_dict.items():
        if key != 'entry_type' and key != 'key':  # @article{Sh:155,
            bibtex_lines.append('\t{0} = "{1}"'.format(key, value))
    return ',\n'.join(bibtex_lines) + '\n}'  # TODO check produced month format


def get_citation(bibtex_dict):  # TODO
    pass


def add_biblio_item(POST_data, conn, c):
    '''
    Adds single biblio record to the table bibliography
    :param POST_data: must contain the fields:  bibtex_json (TEXT),
                                                added_by (INTEGER),
                                                abbreviation (TEXT)
    '''
    bibtex_dict = json.loads(POST_data['bibtex_json'])
    c.execute(
        """INSERT INTO bibliography (
              abbreviation,
              description,
              added_by
              )
           VALUES (?,?,?)""", (POST_data['abbreviation'],
                               POST_data['bibtex_json'],  # TODO what format of data expected - bibtex_str or json_str
                               POST_data['added_by'])
        )
    conn.commit()
    # extract_biblio_table(c) # TODO figure out what it does