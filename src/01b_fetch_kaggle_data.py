#!/usr/bin/env python
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

DEST_DIR = Path().absolute().parent / 'data' / '01_raw' / 'kaggle'
DEST_DIR.mkdir(exist_ok=True, parents=True)

api = KaggleApi()

api.authenticate()
api.dataset_download_files('PromptCloudHQ/australian-job-listings-data-from-seek-job-board', path=DEST_DIR, quiet=False, unzip=True)
api.dataset_download_files('PromptCloudHQ/australian-jobs-on-gumtreecomau', path=DEST_DIR, quiet=False, unzip=True)
