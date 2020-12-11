import logging
import re
from typing import Union

import bs4
from lib.normalise import (
    WOF_AUS,
    WOF_NZ,
    Geocoder,
    datetime_from_iso_utc,
    html2plain,
)
from lib.salary import get_salary_data

from .abstract_datasource import AbstractDatasource

AU_GEOCODER = Geocoder(lang="en", filter_country_ids=(WOF_AUS, WOF_NZ))

# PROBONO_MAPPINGS = {
#     'Organisation :': 'hiringOrganization',
#     'Location :': 'jobLocation',
#     'Sector :': 'industry',
#     'Salary type :': 'baseSalary_unit', # TODO ??
#     'Work type :': 'employmentType',
#     'Profession :': 'occupationalCategory',
#     'Salary :': 'baseSalary',
#     'Application closing date :': 'validThrough',
# }


def fix_probono_location(loc):
    return re.sub(r"(.*)\((.*)\)", "\\2, \\1", loc)


class Datasource(AbstractDatasource):
    name = "probono"

    def extract(self, html: Union[bytes, str], uri, view_date):
        soup = bs4.BeautifulSoup(html, "html5lib")
        infos = soup.select(".org-basic-info > div > p.org-add")
        data = {}
        for info in infos:
            key = info.select_one("b")
            if not key:
                logging.warning("Missing key in %s; %s", uri, info)
                continue
            schema_key = key.get_text().strip()
            value = "".join(
                str(s.get_text() if isinstance(s, bs4.element.Tag) else s).strip()
                for s in key.next_siblings
            )
            data[schema_key] = value
        description = str(soup.select_one("#about-role") or "")
        hiringOrganization_description = str(
            soup.select_one("#about-organisation") or ""
        )
        header = soup.select_one("h1")
        if not header:
            logging.warning("Missing header: %s", uri)
            title = None
        else:
            title = header.get_text().strip()
        return [
            {
                "title": title,
                "description": description,
                "organisation_description": hiringOrganization_description,
                "metadata": data,
                "uri": uri,
                "view_date": view_date,
            }
        ]

    def normalise(
        self, title, description, organisation_description, metadata, uri, view_date
    ):
        salary_text = metadata.get("Salary :")
        salary_data = get_salary_data(salary_text)
        location_raw = metadata["Location :"]
        return {
            "title": title,
            "description": html2plain(description),
            "uri": uri,
            "view_date": datetime_from_iso_utc(view_date),
            "org": metadata.get("Organisation :"),
            **salary_data,
            "location_raw": location_raw,
            **AU_GEOCODER.geocode(fix_probono_location(location_raw)),
        }
