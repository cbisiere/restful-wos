# For compatibility with Py2.7
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

def to_ris_text(entries):
    """
    Convert publication information from WoS XML to RIS format.

    Example
    ==========
    ```python
    ris_recs = wos_parser.rec_info_to_ris(parsed_recs)
    wos_parser.to_ris_text(ris_recs)
    ```

    Parameters
    ==========
    * entries: list, of WoS pubinfo dict entries in RIS format

    Returns
    ==========
    * str, representing publication info in RIS format
    """
    out = StringIO()

    # Markers to indicate WoS sourced RIS file
    out.write("FN Clarivate Analytics Web of Science\n")
    out.write("VR 1.0\n")

    for ent in entries:
        for k, v in ent.items():
            if isinstance(v, list):
                v = [i for i in v if i != ', ' and i is not None]
                v = "\n   ".join(v)
            out.write("{} {}\n".format(k, v))
        # End for
        out.write("ER\n\n")  # End of record marker
    # End for

    return out.getvalue()
# End to_ris_text()
