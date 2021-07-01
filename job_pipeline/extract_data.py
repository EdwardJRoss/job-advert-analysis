#!/usr/bin/env python
import logging
from pathlib import Path
from typing import List

import job_pipeline.sources.careers_vic
import job_pipeline.sources.cgcrecruitment
import job_pipeline.sources.csiro
import job_pipeline.sources.davidsonwp
import job_pipeline.sources.engineeringjobs
import job_pipeline.sources.ethicaljobs
import job_pipeline.sources.gumtree
import job_pipeline.sources.iworkfornsw
import job_pipeline.sources.kaggle_datascienceau_201910
import job_pipeline.sources.kaggle_promptcloud_gumtree
import job_pipeline.sources.kaggle_promptcloud_latest
import job_pipeline.sources.kaggle_promptcloud_listings
import job_pipeline.sources.launchrecruitment
import job_pipeline.sources.probono
import job_pipeline.sources.seek
from job_pipeline.sources.abstract_datasource import AbstractDatasource

DATASOURCES: List[AbstractDatasource] = [
    job_pipeline.sources.careers_vic.Datasource(),
    job_pipeline.sources.cgcrecruitment.Datasource(),
    job_pipeline.sources.csiro.Datasource(),
    job_pipeline.sources.davidsonwp.Datasource(),
    job_pipeline.sources.engineeringjobs.Datasource(),
    job_pipeline.sources.ethicaljobs.Datasource(),
    job_pipeline.sources.gumtree.Datasource(),
    job_pipeline.sources.iworkfornsw.Datasource(),
    job_pipeline.sources.launchrecruitment.Datasource(),
    job_pipeline.sources.probono.Datasource(),
    job_pipeline.sources.seek.Datasource(),
    job_pipeline.sources.kaggle_promptcloud_listings.Datasource(),
    job_pipeline.sources.kaggle_promptcloud_gumtree.Datasource(),
    job_pipeline.sources.kaggle_promptcloud_latest.Datasource(),
    job_pipeline.sources.kaggle_datascienceau_201910.Datasource(),
]

INPUT = Path("../data/01_raw")
OUTPUT = Path("../data/02_primary")

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)

    for datasource in DATASOURCES:
        datasource.extract_all(INPUT / datasource.name, OUTPUT / datasource.name)
