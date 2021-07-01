import logging
from io import BytesIO
from multiprocessing import Pool
from pathlib import Path
from typing import Any, Dict, Generator, List

from tqdm import tqdm
from warcio.archiveiterator import ArchiveIterator
from warcio.recordloader import ArcWarcRecord
from warcio.warcwriter import WARCWriter

from job_pipeline.lib.cc import CrawlResultDict, cdx_query, fetch_cc
from job_pipeline.lib.io import AtomicFileWriter
from job_pipeline.sources.abstract_datasource import AbstractDatasource

_DEFAULT_NTHREAD = 32


def fetch_source_rows(
    api: str, query: str, query_filters: List[str]
) -> List[CrawlResultDict]:
    assert query.endswith("*")
    return list(cdx_query(api, query, query_filters))


def fetch_cc_row(row: CrawlResultDict) -> bytes:
    return fetch_cc(row["filename"], int(row["offset"]), int(row["length"]))


def fetch_all_cc(
    sources: List[CrawlResultDict],
    nthread: int = _DEFAULT_NTHREAD,
    disable_progress: bool = False,
) -> Generator[ArcWarcRecord, None, None]:
    with Pool(nthread) as p:
        for content in tqdm(
            p.imap_unordered(fetch_cc_row, sources),
            total=len(sources),
            disable=disable_progress,
        ):
            archive_iterator = ArchiveIterator(BytesIO(content))
            # Assume exactly one record
            warc = next(archive_iterator)
            yield warc


def read_warc_responses(
    filename: Path, disable_progress: bool = False
) -> Generator[ArcWarcRecord, None, None]:
    with open(filename, "rb") as stream:
        for record in tqdm(ArchiveIterator(stream)):
            assert record.rec_type == "response"
            yield record


class CommonCrawlDatasource(AbstractDatasource):

    query: str
    query_filters: List[str] = []
    # Number of threads for parallel
    nthread: int = _DEFAULT_NTHREAD
    disable_progress: bool = False

    raw_extension = ".warc.gz"

    sources = {
        "CC-MAIN-2020-50": "https://index.commoncrawl.org/CC-MAIN-2020-50-index",
        "CC-MAIN-2020-45": "https://index.commoncrawl.org/CC-MAIN-2020-45-index",
        "CC-MAIN-2020-40": "https://index.commoncrawl.org/CC-MAIN-2020-40-index",
        "CC-MAIN-2020-34": "https://index.commoncrawl.org/CC-MAIN-2020-34-index",
        "CC-MAIN-2020-29": "https://index.commoncrawl.org/CC-MAIN-2020-29-index",
        "CC-MAIN-2020-24": "https://index.commoncrawl.org/CC-MAIN-2020-24-index",
        "CC-MAIN-2020-16": "https://index.commoncrawl.org/CC-MAIN-2020-16-index",
    }

    def fetch_source_rows(self, source: str) -> List[CrawlResultDict]:
        return fetch_source_rows(source, self.query, self.query_filters)

    def download_one(self, path: Path, source: str) -> None:
        logging.info(f"Fetching {source} for {self.name}")
        source_rows = self.fetch_source_rows(source)
        with AtomicFileWriter(path) as output:
            writer = WARCWriter(output, gzip=True)
            logging.info(f"Downloading {source}")
            for warc in fetch_all_cc(source_rows, self.nthread, self.disable_progress):
                writer.write_record(warc)

    def extract(self, html: bytes, uri: str, view_date: str) -> List[Dict[Any, Any]]:
        pass

    def extract_one(self, path: Path) -> Generator[Dict[Any, Any], None, None]:
        for warc in read_warc_responses(path):
            html = warc.content_stream().read()
            uri = warc.rec_headers["WARC-Target-URI"]
            view_date = warc.rec_headers["WARC-Date"]

            assert uri is not None
            assert view_date is not None

            for result in self.extract(html, uri, view_date):
                yield result
