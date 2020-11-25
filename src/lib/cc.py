import json
import logging
from functools import lru_cache

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def jsonl_loads(jsonl):
    return [json.loads(line) for line in jsonl.splitlines()]

INDEXES_URL = 'https://index.commoncrawl.org/collinfo.json'
@lru_cache(maxsize=1)
def get_indexes():
    r = requests.get(INDEXES_URL)
    r.raise_for_status()
    return r.json()

def cdx_num_pages(api, query, filters=None):
    r = requests.get(api,
                 params = {
                     'url': query,
                     'output': 'json',
                     'showNumPages': True,
                     'filter': filters or [],
                 })
    r.raise_for_status()
    data = r.json()
    return data['pages']

def cdx_query_page(api, query, page=0, filters=None):
    r = requests.get(api,
                     params = {
                     'url': query,
                     'output': 'json',
                     'filter': filters or [],
                     'page': page
                     })
    if r.status_code == 404:
        logging.warning('No results found for %s in %s', query, api)
        return []
    r.raise_for_status()
    results = jsonl_loads(r.text)
    return results

def cdx_query(api, query, filters=None):
    filters = ['=status:200'] + (filters or [])
    for page in range(cdx_num_pages(api, query, filters)):
        for result in cdx_query_page(api, query, page, filters):
            yield result


# TODO: This should all be wrapped in an object rather than a global
CC_DATA_URL = 'https://commoncrawl.s3.amazonaws.com/'
RETRY_STRATEGY = Retry(
    total=5,
    backoff_factor=1
)
ADAPTER = HTTPAdapter(max_retries=RETRY_STRATEGY)
CC_HTTP = requests.Session()
CC_HTTP.mount(CC_DATA_URL, ADAPTER)


def fetch_cc(filename: str, offset: int, length: int) -> bytes:
    data_url = CC_DATA_URL + filename
    start_byte = int(offset)
    end_byte = start_byte + int(length)
    headers = {'Range': f'bytes={start_byte}-{end_byte}'}
    r = CC_HTTP.get(data_url, headers=headers)
    r.raise_for_status()
    return r.content
