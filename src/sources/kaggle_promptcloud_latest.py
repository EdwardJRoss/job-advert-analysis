import datetime
import json
from pathlib import Path
from typing import Any, Dict, Generator

from lib.normalise import WOF_AUS, WOF_NZ, Geocoder
from lib.salary import get_salary_data
from sources.abstract_datasource import module_name
from sources.kaggle_datasource import KaggleDatasource

AU_GEOCODER = Geocoder(lang="en", filter_country_ids=(WOF_AUS, WOF_NZ))


class Datasource(KaggleDatasource):
    # License: CC0: Public Domain
    dataset = "promptcloud/latest-seek-australia-job-dataset"
    sources = {
        "seekau_2019q3": "marketing_sample_for_seek_au-jobs_listing__20190901_20191231__10k_data.json"
    }
    name = module_name(__name__)

    raw_extension = ".json"

    def extract_one(self, path: Path) -> Generator[Dict[Any, Any], None, None]:
        with open(path, "r") as f:
            for line in f:
                yield json.loads(line)

    def normalise(self, *args, **data) -> Dict[str, Any]:
        location_text = ", ".join(
            [
                data["city"],
                data["state"],
                data.get("country") or data["inferred_country"],
            ]
        )
        salary_text = data.get("salary_offered")
        return {
            "title": data["job_title"],
            "description": data["job_description"],
            "uri": data["url"],
            "view_date": datetime.datetime.strptime(
                data["crawl_timestamp"], "%Y-%m-%d %H:%M:%S +0000"
            ),
            "org": data["company_name"],
            **get_salary_data(salary_text),
            "location_raw": location_text,
            **AU_GEOCODER.geocode(location_text),
        }
