#!/usr/bin/env python
import logging
from pathlib import Path
from typing import List

import sources.careers_vic
import sources.cgcrecruitment
import sources.csiro
import sources.davidsonwp
import sources.engineeringjobs
import sources.ethicaljobs
import sources.gumtree
import sources.iworkfornsw
import sources.kaggle_datascienceau_201910
import sources.kaggle_promptcloud_gumtree
import sources.kaggle_promptcloud_latest
import sources.kaggle_promptcloud_listings
import sources.launchrecruitment
import sources.probono
import sources.seek
from sources.abstract_datasource import AbstractDatasource

DATASOURCES: List[AbstractDatasource] = [
    sources.careers_vic.Datasource(),
    sources.cgcrecruitment.Datasource(),
    sources.csiro.Datasource(),
    sources.davidsonwp.Datasource(),
    sources.engineeringjobs.Datasource(),
    sources.ethicaljobs.Datasource(),
    sources.gumtree.Datasource(),
    sources.iworkfornsw.Datasource(),
    sources.launchrecruitment.Datasource(),
    sources.probono.Datasource(),
    sources.seek.Datasource(),
    sources.kaggle_promptcloud_listings.Datasource(),
    sources.kaggle_promptcloud_gumtree.Datasource(),
    sources.kaggle_promptcloud_latest.Datasource(),
    sources.kaggle_datascienceau_201910.Datasource(),
]


INPUT = Path("../data/02_primary")
OUTPUT = Path("../data/03_secondary")

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)

    for datasource in DATASOURCES:
        datasource.normalise_all(INPUT / datasource.name, OUTPUT / datasource.name)
