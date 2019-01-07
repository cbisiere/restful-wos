import requests
import json
import yaml

from extractor import extract_ris
from converter import to_ris_text

class WoSRESTClient(object):

    BASE_URL = "https://api.clarivate.com/api/wos"

    def __init__(self, apikey):
        self.apikey = apikey

        self._req_header = {
            'X-ApiKey': apikey,
            'content-type': 'application/json',
        }
    
    def query(self, query_string, time_span=None, **kwargs):
        defaults = {
            'databaseId': 'WOK',
            'lang': 'en',
            'edition': 'WOS+SCI',
            'firstRecord': 1,
            'count': 100,
            'sort': 'PY',
            'optionView': 'FR'
        }

        search = kwargs if kwargs else {}
        for kw in defaults:
            if kw not in kwargs:
                search.update({kw: defaults[kw]})

        search.update({
            'usrQuery': query_string,
        })

        if time_span:
            search.update({'publishTimeSpan': '{}+{}'.format(time_span[0], time_span[1])})

        # Get first 100 records
        resp_data = self.send_query(search)
        results = resp_data['QueryResult']
        num_records = results['RecordsFound']
        print("num records", num_records)

        ris_entries = []
        ris_entries = extract_ris(resp_data, ris_entries)
            
        return ris_entries
        
        # Need to request more
        while search['firstRecord'] <= num_records:
            break
            search.update({'firstRecord': search['firstRecord'] + 100})
            resp_data = self.send_query(search)
            ris_entries = extract_ris(resp_data, ris_entries)

            # parse results and combine
        
        return ris_entries
    # End query()
    
    def send_query(self, search):
        response = requests.get(self.BASE_URL, params=search, headers=self._req_header)
        if response.status_code != 200:
            raise ValueError("Error when sending query.\nStatus Code: {}\nMessage: {}".format(
                response.status_code,
                response.text
            ))
        
        return response.json()
    # End send_query()

    
if __name__ == '__main__':

    print("Starting!")

    with open('config.yml', 'r') as fp:
        config = yaml.load(fp)['restful_wos']

    client = WoSRESTClient(config['wos_expanded'])
    resp = client.query('TS=(uncertain* AND (catchment OR watershed or water))',
                 time_span=('2018-01-01', '2018-12-31'))
    
    with open('rest_dev.txt', 'w') as fp:
        json.dump(resp, fp)

    print(to_ris_text(resp))

    print("Finished!")
