from io import BytesIO
from multiprocessing import Pool
import logging
from typing import Generator, Iterable
from pathlib import Path
import csv
import pandas as pd
from warcio.recordloader import ArcWarcRecord
from warcio.archiveiterator import ArchiveIterator
from warcio.warcwriter import WARCWriter
from lib.cc import fetch_cc
from lib.io import AtomicFileWriter
from tqdm import tqdm

DEST_DIR = Path('../data/01_raw')

INDEX_DIR = Path('../data/00_sources')


def index_files():
    return list(INDEX_DIR.glob('*/*.csv'))

def fetch_cc_row(row):
    return fetch_cc(row['filename'], row['offset'], row['length'])

def download_from_index_file(path: Path, nthread: int=32) -> Generator[ArcWarcRecord, None, None]:
    with open(path, 'rt') as f:
        rows = list(csv.DictReader(f))
    nrow = len(rows)
    logging.info('Processing %s rows', nrow)
    with Pool(nthread) as p:
        for content in tqdm(p.imap_unordered(fetch_cc_row, rows), total=nrow):
            archive_iterator = ArchiveIterator(BytesIO(content))
            # Assume exactly one record
            warc = next(archive_iterator)
            yield warc


SOURCES = Path('./sources.csv')


def read_sources():
    with SOURCES.open('rt') as f:
        sources = list(csv.DictReader(f))
    return sources


def source_name_to_warc_gz(path: Path, outdir: Path) -> Path:
    parent = path.parent.name
    fname = path.name
    assert fname.endswith('.csv')
    fname = fname[:-4] + '.warc.gz'
    return outdir / parent / fname


def write_source(source, dest_name):
    warcs = download_from_index_file(source)
    with AtomicFileWriter(dest_name, 'wb') as output:
        writer = WARCWriter(output, gzip=True)
        for warc in warcs:
            writer.write_record(warc)


def download_sources(sources, dest_dir):
    for source in sources:
        dest_name = source_name_to_warc_gz(source, dest_dir)
        if dest_name.exists():
            logging.info('Skipping %s: Destination Exists', source)
            continue
        logging.info('Processing %s', source)
        dest_name.parent.mkdir(exist_ok=True)
        write_source(source, dest_name)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    DEST_DIR.mkdir(parents=True, exist_ok=True)
    download_sources(index_files(), DEST_DIR)



