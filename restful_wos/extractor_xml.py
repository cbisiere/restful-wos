import re as _re

def extract_wos_xml_element(data, element_name, attr=None, content_only=True):
    '''
    Extract an xml element from a string containing xml data returned by WoS.

    An optionnal attribute and its value can be specified.

    For the sake of efficiency, this function does not use full xml parsing .
    Data in the string is assumed to be regular enough to be parsed
    using simple regular expression, thus avoiding cosly xml parsing of
    potentialy huge xml documents. Or course, this may break in rare, weird
    cases.

    Args:
        data (string): Xml data
        element_name (string): Name of the xml element to look for
        attr (tuple): Attribute (name, value) of this element or None
        content_only (bool): True if the opening and closing tags must
            not be returned.
    Returns:
        sting or None: The element found or None

    '''
    attr_pattern = r' {0}="{1}"'.format(attr[0], attr[1]) if attr is not None else ''
    pattern = r'<{0}{1}>\s*(.*?)\s*</{0}>'.format(element_name, attr_pattern)
    res = _re.search(pattern, data, _re.S)
    if res is None:
        return None
    return res.group(1 if content_only else 0)

def extract_xml(data, entries=None):
    '''
    Append to an existing list of entries all the publication records
    contained in a piece of xml data.

    For the sake of efficiency, a single sequence of a <records>
    element containing one or more <REC> elements is appended to the list, as
    the primary use case leads to concatenate all the entries in a single
    <records> element.

    Args:
        data (string): Xml response sent by WoS
        entries (list): The list of existing extractions, each being a string
            containing a <records> element containing one or more <REC> elements

    Returns:
        list: the updated list of entries
    '''
    if not entries:
        entries = []

    res = extract_wos_xml_element(data, 'records', content_only=False)
    if res is None:
        print("WoS: Unexpected return format:")
        print(data)
        return entries

    if res.count('<REC ') == 0:
        print("WoS: No records found!")
        return entries

    entries.append(res)

    return entries
