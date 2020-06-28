from io import BytesIO
import json
from functools import lru_cache
import requests
from warcio.archiveiterator import ArchiveIterator
from warcio.recordloader import ArcWarcRecord

def jsonl_loads(jsonl):
    return [json.loads(line) for line in jsonl.splitlines()]

INDEXES_URL = 'https://index.commoncrawl.org/collinfo.json'
@lru_cache(maxsize=1)
def get_indexes():
    r = requests.get(INDEXES_URL)
    r.raise_for_status()
    return r.json()

def cdx_num_pages(api, query):
    r = requests.get(api,
                 params = {
                     'url': query,
                     'output': 'json',
                     'showNumPages': True,
                 })
    data = r.json()
    return data['pages']

def cdx_query_page(api, query, page=0):
    r = requests.get(api,
                     params = {
                     'url': query,
                     'output': 'json',
                     'filter': ['=status:200'],
                     'page': page
                     })
    r.raise_for_status()
    results = jsonl_loads(r.text)
    return results

def cdx_query(api, query):
    for page in range(cdx_num_pages(api, query)):
        for result in cdx_query_page(api, query, page):
            yield result


CC_DATA_URL = 'https://commoncrawl.s3.amazonaws.com/'
def fetch_cc(filename: str, offset: int, length: int) -> ArcWarcRecord:
    data_url = CC_DATA_URL + filename
    start_byte = int(offset)
    end_byte = start_byte + int(length)
    headers = {'Range': f'bytes={start_byte}-{end_byte}'}
    r = requests.get(data_url, headers=headers)
    archive_iterator = ArchiveIterator(BytesIO(r.content))
    # Assume exactly one record
    warc = next(archive_iterator)
    return warc


