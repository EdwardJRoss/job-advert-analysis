#!/usr/bin/env python
import logging
import pandas as pd
import json
from pathlib import Path
from lib.extract import normalise_warc
from tqdm import tqdm

INPUT = Path('../data/02_primary')
OUTPUT = Path('../data/03_secondary')

def read_input(filename):
    with open(filename, 'r') as f:
        for line in tqdm(f):
            yield json.loads(line)

SOURCES = Path('./sources.csv')
def read_sources():
    return pd.read_csv(SOURCES).set_index('key')

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    OUTPUT.mkdir(exist_ok=True)

    sources = read_sources()

    input_ext = '.jsonl'
    input_paths = list(INPUT.glob(f'*/*{input_ext}'))

    for path in input_paths:
        source_key = path.parent.name
        source_crawl = path.name[:-len(input_ext)]
        source_row = sources.loc[source_key]
        dest_file = OUTPUT / source_key / (source_crawl + '.feather')
        if dest_file.exists():
            logging.info('Skipping %s from %s with %s', path, source_key, source_row['parser'])
            continue
        dest_file.parent.mkdir(exist_ok=True)

        logging.info('Processing %s from %s with %s', path, source_key, source_row['parser'])
        source_data = read_input(path)

        df = pd.DataFrame([normalise_warc(datum, source_row['parser']) for datum in source_data])
        df.to_feather(dest_file)
