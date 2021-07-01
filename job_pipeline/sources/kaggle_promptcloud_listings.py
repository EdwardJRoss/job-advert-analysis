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
    # License: CC BY-SA 4.0
    dataset = "PromptCloudHQ/australian-job-listings-data-from-seek-job-board"
    sources = {"seekau": "seek_australia_sample.csv"}
    raw_extension = ".csv"
    name = module_name(__name__)

    def extract_one(self, path: Path) -> Generator[Dict[Any, Any], None, None]:
        with open(path, "r", encoding="latin-1") as f:
            for row in csv.DictReader(f):
                yield row

    def normalise(self, *args, **data) -> Dict[str, Any]:
        parts = [x for x in [data.get("city"), data.get("state"), data.get("geo")] if x]
        location_text = ", ".join(parts)
        return {
            "title": data["job_title"],
            "description": data["job_description"],
            "uri": data["pageurl"],
            "view_date": datetime.datetime.strptime(
                data["crawl_timestamp"], "%Y-%m-%d %H:%M:%S +0000"
            ),
            "org": data["company_name"],
            **get_salary_data(data.get("salary_offered")),
            "location_raw": location_text,
            **AU_GEOCODER.geocode(location_text),
        }
