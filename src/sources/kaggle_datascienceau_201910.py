import csv
import datetime
from pathlib import Path
from typing import Any, Dict, Generator

from lib.normalise import WOF_AUS, WOF_NZ, Geocoder
from sources.abstract_datasource import module_name
from sources.kaggle_datasource import KaggleDatasource

AU_GEOCODER = Geocoder(lang="en", filter_country_ids=(WOF_AUS, WOF_NZ))


class Datasource(KaggleDatasource):
    # License: CC0: Public Domain
    dataset = "santokalayil/data-scientist-jobs-in-australia-october-25-2019"
    sources = {
        "indeedau_datascience_202010": "datascientist_jobs_in_australia_Oct_25_2019.csv"
    }
    raw_extension = ".csv"
    name = module_name(__name__)

    def extract_one(self, path: Path) -> Generator[Dict[Any, Any], None, None]:
        with open(path, "r", encoding="latin-1") as f:
            for row in csv.DictReader(f):
                yield {k: v for k, v in row.items() if k}

    def normalise(self, *args, **data) -> Dict[str, Any]:
        return {
            "title": data["title"],
            "description": data["summary"],
            "view_date": datetime.datetime(2019, 10, 25),
            "org": data["company"],
            "location_raw": data["location"],
            **AU_GEOCODER.geocode(data["location"]),
        }
