import requests
import json
import yaml
import time
import math
from tqdm import tqdm

from extractor import extract_ris
from converter import to_ris_text, write_file

class WoSRESTClient(object):

    BASE_URL = "https://api.clarivate.com/api/wos"
    defaults = {
        'databaseId': 'WOK',
        'lang': 'en',
        'edition': 'WOS+SCI',
        'firstRecord': 1,
        'count': 100,
        'sort': 'PY',
        'optionView': 'FR'
    }

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
        defaults = self.defaults
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
        result_info = resp_data['QueryResult']
        num_records = result_info['RecordsFound']
        print("Found {} records, retrieving in batches of 100".format(num_records))

        ris_entries = []
        # Strangely, the initial request return has 'Data', but
        # subsequent requests do not.
        ris_entries = extract_ris(resp_data['Data'], ris_entries)

        if num_records > 100:
            # Need to request more
            query_id = result_info["QueryID"]

            num_requests = int(math.ceil(num_records / 100.0))
            with tqdm(total=num_requests, unit='requests') as pbar:
                pbar.update(1)  # we've already done 1 request
                while search['firstRecord'] <= num_records:
                    search.update({'firstRecord': search['firstRecord'] + 100})

                    resp_data = self.send_query(search, url='{}/query/{}'.format(self.BASE_URL, query_id))
                    if 'Records' not in resp_data:
                        print("Unexpected return format:")
                        print(resp_data)
                        breakpoint()
                    ris_entries = extract_ris(resp_data, ris_entries)

                    pbar.update(1)
        
        return ris_entries
    # End query()
    
    def send_query(self, search, url=None):
        if not url:
            url = self.BASE_URL
        response = requests.get(url, params=search, headers=self._req_header)
        status = response.status_code
        if status != 200:
            if status == 504:
                # timeout error
                response = self._handle_timeout(search, url)
            else:
                print("RAW:", str(response.headers))
                raise ValueError("Error when sending query.\nStatus Code: {}\nMessage: {}\nParams: {}".format(
                    response.status_code,
                    response.text,
                    search
                ))

        return response.json()
    # End send_query()

    def _handle_timeout(self, search, url):
        time.sleep(5)  # wait 5 seconds...
        return self.send_query(search, url)

    
if __name__ == '__main__':

    print("Starting!")

    with open('config.yml', 'r') as fp:
        config = yaml.load(fp)['restful_wos']

    client = WoSRESTClient(config['wos_expanded'])
    resp = client.query('TS=(uncertain* AND (catchment OR watershed OR water))',
                 time_span=('2017-01-01', '2018-12-31'))

    write_file(to_ris_text(resp), 'ris_output', overwrite=True)

    print("Finished!")
