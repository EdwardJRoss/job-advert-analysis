import json
import logging
from functools import lru_cache
from typing import Dict, Generator, List, Optional, Union

import requests
from mypy_extensions import TypedDict
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def jsonl_loads(jsonl):
    return [json.loads(line) for line in jsonl.splitlines()]


INDEXES_URL = "https://index.commoncrawl.org/collinfo.json"

# TODO: This should all be wrapped in an object rather than a global
CC_DATA_URL = "https://data.commoncrawl.org/"
RETRY_STRATEGY = Retry(total=5, backoff_factor=1, status_forcelist=set([504, 500]))
ADAPTER = HTTPAdapter(max_retries=RETRY_STRATEGY)
CC_HTTP = requests.Session()
CC_HTTP.mount(CC_DATA_URL, ADAPTER)

CC_INDEX = requests.Session()
CC_INDEX.mount("https://index.commoncrawl.org/", ADAPTER)


CrawlIndexDict = TypedDict(
    "CrawlIndexDict", {"id": str, "name": str, "timegate": str, "cdx-api": str}
)
CrawlResultDict = TypedDict(
    "CrawlResultDict",
    {
        "urlkey": str,
        "timestamp": str,
        "mime": str,
        "status": str,
        "offset": str,
        "filename": str,
        "mime-detected": str,
        "digest": str,
        "redirect": str,
        "url": str,
        "length": str,
    },
)


@lru_cache(maxsize=1)
def get_indexes() -> List[CrawlIndexDict]:
    r = CC_INDEX.get(INDEXES_URL)
    r.raise_for_status()
    return r.json()


def cdx_num_pages(api: str, query: str, filters: Optional[List[str]] = None) -> int:
    params: Dict[str, Union[str, bool, List[str]]] = {
        "url": query,
        "output": "json",
        "showNumPages": True,
        "filter": filters or [],
    }
    r = CC_INDEX.get(
        api,
        params=params,
    )
    r.raise_for_status()
    data = r.json()
    return data["pages"]


def cdx_query_page(
    api: str, query: str, page: int = 0, filters: Optional[List[str]] = None
) -> List[CrawlResultDict]:
    params: Dict[str, Union[str, int, List[str]]] = {
        "url": query,
        "output": "json",
        "filter": filters or [],
        "page": page,
    }
    r = CC_INDEX.get(
        api,
        params=params,
    )
    if r.status_code == 404:
        logging.warning("No results found for %s in %s", query, api)
        return []
    r.raise_for_status()
    results = jsonl_loads(r.text)
    return results


def cdx_query(
    api: str, query: str, filters: Optional[List[str]] = None
) -> Generator[CrawlResultDict, None, None]:
    filters = ["=status:200"] + (filters or [])
    num_pages = cdx_num_pages(api, query, filters)
    for page in range(num_pages):
        logging.debug(f"Querying page {page} of {num_pages} for {query} on {api}")
        for result in cdx_query_page(api, query, page, filters):
            yield result


def fetch_cc(filename: str, offset: int, length: int) -> bytes:
    data_url = CC_DATA_URL + filename
    start_byte = int(offset)
    end_byte = start_byte + int(length)
    headers = {"Range": f"bytes={start_byte}-{end_byte}"}
    r = CC_HTTP.get(data_url, headers=headers)
    r.raise_for_status()
    return r.content
