#!/usr/bin/env python
import logging
from pathlib import Path
from typing import List

import typer

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

RAW_DATA_DIR = Path("./data/01_raw")
EXTRACT_DATA_DIR = Path("./data/02_primary")
NORMALISED_DATA_DIR = Path("./data/03_secondary")


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


app = typer.Typer()


@app.command()
def build(overwrite: bool = False):
    """Run the whole pipeline"""
    fetch(overwrite)
    extract(overwrite)
    normalise(overwrite)


@app.command()
def fetch(overwrite: bool = False):
    """1 - Fetch the data"""
    for datasource in DATASOURCES:
        datasource.download(RAW_DATA_DIR / datasource.name, overwrite=overwrite)


@app.command()
def extract(overwrite: bool = False):
    """2 - Extract Fetched Data"""
    for datasource in DATASOURCES:
        datasource.extract_all(
            RAW_DATA_DIR / datasource.name,
            EXTRACT_DATA_DIR / datasource.name,
            overwrite=overwrite,
        )


@app.command()
def normalise(overwrite: bool = False):
    """3 - Normalise Extracted Data"""
    for datasource in DATASOURCES:
        datasource.normalise_all(
            EXTRACT_DATA_DIR / datasource.name,
            NORMALISED_DATA_DIR / datasource.name,
            overwrite=overwrite,
        )


if __name__ == "__main__":
    # TODO: Logging configuration
    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)
    app()
