#!/usr/bin/env python
import logging
import pandas as pd
import json
from pathlib import Path
from warcio.archiveiterator import ArchiveIterator
from lib.io import AtomicFileWriter
from lib.extract import extract_warc
from tqdm import tqdm

INPUT = Path('../data/01_raw')
OUTPUT = Path('../data/02_primary')

def read_input(filename):
    with open(filename, 'rb') as stream:
        for record in tqdm(ArchiveIterator(stream)):
            assert record.rec_type == 'response'
            yield record

SOURCES = Path('./sources.csv')
def read_sources():
    return pd.read_csv(SOURCES).set_index('key')

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    OUTPUT.mkdir(exist_ok=True)

    sources = read_sources()

    input_ext = '.warc.gz'
    input_paths = list(INPUT.glob(f'*/*{input_ext}'))

    for path in input_paths:
        source_key = path.parent.name
        source_crawl = path.name[:-len(input_ext)]
        source_row = sources.loc[source_key]
        dest_file = OUTPUT / source_key / (source_crawl + '.jsonl')
        if dest_file.exists():
            logging.info('Skipping %s from %s with %s', path, source_key, source_row['parser'])
            continue
        dest_file.parent.mkdir(exist_ok=True)

        logging.info('Processing %s from %s with %s', path, source_key, source_row['parser'])
        source_data = read_input(path)

        data = (job_post for datum in source_data for job_post in extract_warc(datum, source_row['parser']))

        with AtomicFileWriter(dest_file) as f:
            for datum in data:
                line = json.dumps(datum)
                line += '\n'
                bline = line.encode('utf-8')
                f.write(bline)
