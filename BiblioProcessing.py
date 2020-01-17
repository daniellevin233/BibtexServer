import json

'''
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


def get_abbreviation(title):  # TODO
    return "ABBREVIATION"


def get_bibtex_dict(bibtex_str):  # TODO
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


def get_citation(bibtex_dict):  # TODO
    pass


def add_biblio_item(POST_data, conn, c):
    bibtex_dict = get_bibtex_dict(POST_data['bibtex_str'])
    c.execute(
        """INSERT INTO bibliography (
              abbreviation,
              description,
              added_by
              )
           VALUES (?,?,?)""", (
                                get_abbreviation(bibtex_dict['title']),
                                bibtex_dict,  # TODO what format of data expected - bibtex_str or json(dict)
                                POST_data['added_by'])
        )
    conn.commit()
    # extract_biblio_table(c) # TODO figure out what does it do