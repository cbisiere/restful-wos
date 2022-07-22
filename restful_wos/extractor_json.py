def extract_json(data, entries=None):
    if not entries:
        entries = []

    # Parse record set and return
    if 'Records' not in data:
        print("WoS: Unexpected return format:")
        print(data)
        return entries

    if 'records' not in data['Records']:
        print("WoS: No records found for request: {}".format(i))
        return entries

    if 'REC' not in data['Records']['records']:
        print("WoS: No records found!")
        return entries

    for rec in data['Records']['records']['REC']:
        entries.append(rec)

    return entries
