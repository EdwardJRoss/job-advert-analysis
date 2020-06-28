#!/usr/bin/env python
import csv
from pathlib import Path
import pandas as pd
from lib.cc import cdx_query

SOURCES = Path('./sources.csv')
def read_sources():
    with SOURCES.open('rt') as f:
        sources = list(csv.DictReader(f))
    return sources

INDEXES = {
    'CC-MAIN-2020-24': 'https://index.commoncrawl.org/CC-MAIN-2020-24-index',
    'CC-MAIN-2020-16': 'https://index.commoncrawl.org/CC-MAIN-2020-16-index',
}

def write_indexes(sources, indexes, output_dir):
    for idx_key, api in indexes.items():
        for source in sources:
            path = output_dir / source['key'] / f'{idx_key}.csv'
            if path.exists():
                continue
            path.parent.mkdir(exist_ok=True)

            query = source['query']
            assert query.endswith('*')

            # Source
            data = list(cdx_query(api, query))
            df = pd.DataFrame(data)
            df.to_csv(path, index=False)

if __name__ == '__main__':
    OUTPUT_DIR = Path('../data/00_sources')
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sources = read_sources()
    write_indexes(sources, INDEXES, OUTPUT_DIR)
