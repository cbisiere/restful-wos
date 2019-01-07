RIS_TEMPLATE = {
    'TY': None,  # Publication Type
    'AU': None,  # authors
    'AF': None,  # author_fullnames
    'TI': None,  # pubinfo['item']
    'AB': None,  # Abstract
    'SO': None,  # Source (Journal)
    'LA': None,  # Language
    'DT': None,  # Publication type "{} {}".format(pubinfo['pubtype'], pubinfo['doctype'])
    'DE': None,  # Keywords
    'ID': None,  # Keywords Plus (WoS generated keywords)
    'PY': None,  # Publication Year
    'PD': None,  # Sort Date
    'UT': None,  # WoS UID
}

def parse_record(rec_data):
    """Parse record data from API request.

    Parameters
    ==========
    * rec_data : dict, record data returned from request
    """
    tmp = RIS_TEMPLATE.copy()

    static_data = rec_data['static_data']
    dynamic_data = rec_data['dynamic_data']

    summary = static_data['summary']
    pub_info = summary['pub_info']

    authors, fullnames = _extract_authors(summary)
    title, pub_src = _extract_manuscript_info(summary)

    full_metadata = static_data['fullrecord_metadata']

    try:
        abstract = full_metadata['abstracts']['abstract']
        abstract_text = abstract['abstract_text']['p']
    except KeyError:
        abstract = ""
    # End try

    lang = full_metadata['normalized_languages']['language']['content']

    pubtype = summary['pub_info']['pubtype']
    doctype = summary['doctypes']['doctype']

    try:
        kws = full_metadata['keywords']['keyword']
    except KeyError:
        kws = []

    try:
        kws_plus = static_data['item']['keywords_plus']['keyword']
    except KeyError:
        kws_plus = []

    doi = _extract_doi(dynamic_data['cluster_related']['identifiers']['identifier'])

    tmp.update({
        'TY': pub_info['pubtype'],
        'AU': authors,  # authors
        'AF': fullnames,  # author_fullnames
        'TI': title,  # pubinfo['item']
        'AB': abstract_text,  # Abstract
        'SO': pub_src,  # Source (Journal)
        'LA': lang,  # Language
        'DT': "{} {}".format(pubtype, doctype),
        'DE': kws,  # Keywords
        'ID': kws_plus,  # Keywords Plus (WoS generated keywords)
        'PY': pub_info['pubyear'],  # Publication Year
        'PD': pub_info['sortdate'],  # Sort Date
        'UT': rec_data['UID'],  # WoS UID
        'DI': doi,  # DOI or XREF_DOI
    })

    return tmp
# End parse_record()

def extract_ris(data, ris_entries=None):
    if not ris_entries:
        ris_entries = []

    # Parse record set and return
    for idx, rec in enumerate(data['Data']['Records']['records']['REC']):
        rec_dict = parse_record(rec)
        ris_entries.append(rec_dict)
    
    return ris_entries


def _extract_authors(pub_summary):
    authors = []
    author_fullname = []
    pub_names = pub_summary['names']['name']
    if isinstance(pub_names, list):
        for person in pub_names:
            if person['role'].lower() == 'author':
                author_fullname.append(person['full_name'])
                authors.append(person['wos_standard'])
    elif isinstance(pub_names, dict):
        # Only 1 entry
        if pub_names['role'].lower() == 'author':
            author_fullname.append(pub_names['full_name'])
            authors.append(pub_names['wos_standard'])
    # End if
    return authors, author_fullname


def _extract_manuscript_info(summary):
    title = None
    pub_src = None
    for it in summary['titles']['title']:
        if it['type'] == 'item':
            title = it['content']

        if it['type'] == 'source':
            pub_src = it['content']
    return title, pub_src


def _extract_doi(identifiers):
    doi = ""
    for ids in identifiers:
        if ids['type'] == 'doi':
            doi = ids['value']
            break
        elif ids['type'] == 'xref_doi':
            doi = ids['value']
            break
        # End if
    return doi
