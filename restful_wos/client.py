import requests
import json
import yaml
import time
import math
from tqdm.auto import tqdm

from .extractor_ris import extract_ris
from .extractor_xml import extract_xml, extract_wos_xml_element
from .extractor_json import extract_json
from .converter import to_ris_text, write_file


class RESTClient(object):

    BASE_URL = "https://api.clarivate.com/api/wos"
    mime_types = {
        'ris' : 'application/json',
        'json' : 'application/json',
        'xml' : 'application/xml',
    }
    defaults = {
        'databaseId': 'WOS',
        'lang': 'en',
        'edition': 'WOS+SCI',
        'firstRecord': 1,
        'count': 100,
        'sortField': 'PY',
        'optionView': 'FR'
    }

    def __init__(self, config_fn, format = 'ris'):
        # assert isinstance(config, dict), "Give configuration as a dictionary"

        if format not in self.mime_types.keys():
            raise ValueError("Invalid or unsupported format: {}".format(format))
        self._format = format

        with open(config_fn, 'r') as fp:
            config = yaml.safe_load(fp)['restful_wos']

        if 'wos_expanded' in config:
            apikey = config['wos_expanded']
        elif 'wos_lite' in config:
            apikey = config['wos_lite']
        else:
            raise ValueError("No valid API key could be found in given config file!")
        # End if

        self._req_header = {
            'X-ApiKey': apikey,
            'Accept': self.mime_types[format],
        }


    def _prepare_query(self, query_string, time_span=None, **kwargs):
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
        return search

    def records_found(self, query_string, time_span=None, **kwargs):
        search = self._prepare_query(query_string, time_span, **kwargs)
        search.update({
            'count': 0,
        })
        resp_data = self._get_response(search)
        query_id, num_records = self._extract_result_info(resp_data)
        print("WoS: Found {} records".format(num_records))

        return num_records

    def query(self, query_string, time_span=None, **kwargs):
        search = self._prepare_query(query_string, time_span, **kwargs)

        # Get first 100 records
        resp_data = self._get_response(search)
        query_id, num_records = self._extract_result_info(resp_data)
        print("WoS: Found {0} records, retrieving in batches of {1}".format(num_records, search['count']))

        entries = []
        entries = self._extract_data(resp_data, entries)

        REQ_MAX = search['count']
        if num_records > REQ_MAX:
            # Need to request more
            num_requests = int(math.ceil(num_records / REQ_MAX))
            with tqdm(total=num_requests, desc='requesting', unit='requests') as pbar:
                pbar.update(1)  # we've already done 1 request
                while search['firstRecord'] + REQ_MAX <= num_records:
                    search.update(
                        {'firstRecord': search['firstRecord'] + REQ_MAX})

                    resp_data = self._get_response(search, url='{}/query/{}'.format(self.BASE_URL, query_id))
                    entries = self._extract_data(resp_data, entries)

                    pbar.update(1)
                # End while
            # End pbar

        return entries
    # End query()

    def _send_query(self, search, url=None):
        if not url:
            url = self.BASE_URL
        response = requests.get(url, params=search, headers=self._req_header)
        status = response.status_code
        if status != 200:
            if status == 504:
                # timeout error
                response = self._handle_timeout(search, url)
            else:
                raise ValueError("Error when sending query.\nStatus Code: {}\nHeader: {}\n\nMessage: {}\nParams: {}".format(
                    response.status_code,
                    response.headers,
                    response.text,
                    search
                ))

        return response
    # End _send_query()

    def _handle_timeout(self, search, url):
        time.sleep(5)  # wait 5 seconds...
        return self._send_query(search, url)


    def _get_response(self, search, url=None):
        response = self._send_query(search, url)
        return response.text if self._format == 'xml' else response.json()

    def _extract_result_info(self, data):
        if self._format == 'xml':
            query_result = extract_wos_xml_element(data, 'map', ('name', 'QueryResult'))
            query_id = extract_wos_xml_element(query_result, 'val', ('name', 'QueryID'))
            num_records = extract_wos_xml_element(query_result, 'val', ('name', 'RecordsFound'))
            return int(query_id), int(num_records)
        else:
            return data['QueryResult']['QueryID'], \
                data['QueryResult']['RecordsFound']

    def _extract_data(self, resp_data, entries):
        if self._format == 'xml':
            return extract_xml(resp_data, entries)
        else:
            # Strangely, the initial request return has 'Data', but
            # subsequent requests do not.
            if 'Data' in resp_data:
                resp_data = resp_data['Data']
            if self._format == 'ris':
                return extract_ris(resp_data, entries)
            else:
                return extract_json(resp_data, entries)


if __name__ == '__main__':

    print("Starting!")

    with open('config.yml', 'r') as fp:
        config = yaml.safe_load(fp)['restful_wos']

    client = RESTClient('config.yml')
    resp = client.query('TS=(uncertain* AND (catchment OR watershed OR water))',
                 time_span=('2018-06-01', '2018-12-31'))

    write_file(to_ris_text(resp), 'ris_output', overwrite=True)

    print("Finished!")
