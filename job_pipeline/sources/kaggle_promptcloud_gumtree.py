import csv
import datetime
from pathlib import Path
from typing import Any, Dict, Generator

from job_pipeline.lib.normalise import WOF_AUS, WOF_NZ, Geocoder
from job_pipeline.lib.salary import get_salary_data
from job_pipeline.sources.abstract_datasource import module_name
from job_pipeline.sources.kaggle_datasource import KaggleDatasource

AU_GEOCODER = Geocoder(lang="en", filter_country_ids=(WOF_AUS, WOF_NZ))


class Datasource(KaggleDatasource):
    # License: CC BY-NC-SA 4.0
    dataset = "PromptCloudHQ/australian-jobs-on-gumtreecomau"
    sources = {"gumtreeau": "gumtree_com_au-sample.csv"}
    raw_extension = ".csv"
    name = module_name(__name__)

    def extract_one(self, path: Path) -> Generator[Dict[Any, Any], None, None]:
        with open(path, "r") as f:
            for row in csv.DictReader(f):
                yield row

    def normalise(self, *args, **data) -> Dict[str, Any]:
        return {
            "title": data["job_title"],
            "description": data["job_description"],
            "uri": data["page_url"],
            # Not quite true; this is date added
            "view_date": datetime.datetime.strptime(data["date_added"], "%d/%m/%Y"),
            **get_salary_data(data["salary"]),
            "location_raw": data["location"],
            **AU_GEOCODER.geocode(data["location"]),
        }
