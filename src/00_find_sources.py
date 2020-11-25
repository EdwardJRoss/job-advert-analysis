#!/usr/bin/env python
import csv
import logging
from pathlib import Path

import pandas as pd

from lib.cc import cdx_query

SOURCES = Path("./sources.csv")


def read_sources():
    with SOURCES.open("rt") as f:
        sources = list(csv.DictReader(f))
    return sources


INDEXES = {
    "CC-MAIN-2020-24": "https://index.commoncrawl.org/CC-MAIN-2020-24-index",
    "CC-MAIN-2020-16": "https://index.commoncrawl.org/CC-MAIN-2020-16-index",
}


def write_indexes(sources, indexes, output_dir):
    for idx_key, api in indexes.items():
        for source in sources:
            path = output_dir / source["key"] / f"{idx_key}.csv"
            if path.exists():
                logging.info("Skipping %s", path)
                continue
            path.parent.mkdir(exist_ok=True)

            query = source["query"]
            query_filter = source["filter"] or None
            logging.info("Querying %s with filter %s", query, query_filter)
            assert query.endswith("*")

            data = list(cdx_query(api, query, [query_filter]))
            df = pd.DataFrame(data)
            logging.info("Writing %s fetches to %s", len(df), path)
            df.to_csv(path, index=False)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)

    OUTPUT_DIR = Path("../data/00_sources")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sources = read_sources()
    write_indexes(sources, INDEXES, OUTPUT_DIR)
