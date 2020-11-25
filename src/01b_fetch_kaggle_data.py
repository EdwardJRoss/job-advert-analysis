#!/usr/bin/env python
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

DEST_DIR = Path().absolute().parent / "data" / "01_raw" / "kaggle"
DEST_DIR.mkdir(exist_ok=True, parents=True)

api = KaggleApi()

api.authenticate()
# License: CC BY-SA 4.0
api.dataset_download_files(
    "PromptCloudHQ/australian-job-listings-data-from-seek-job-board",
    path=DEST_DIR,
    quiet=False,
    unzip=True,
)
# License: CC BY-NC-SA 4.0
api.dataset_download_files(
    "PromptCloudHQ/australian-jobs-on-gumtreecomau",
    path=DEST_DIR,
    quiet=False,
    unzip=True,
)
# License: CC0: Public Domain
api.dataset_download_files(
    "promptcloud/latest-seek-australia-job-dataset",
    path=DEST_DIR,
    quiet=False,
    unzip=True,
)
# License: "For public usage"
api.dataset_download_files(
    "santokalayil/data-scientist-jobs-in-australia-october-25-2019",
    path=DEST_DIR,
    quiet=False,
    unzip=True,
)
