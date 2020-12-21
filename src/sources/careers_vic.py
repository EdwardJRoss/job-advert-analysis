import logging
import re
from typing import Any, Dict, List, Union

import bs4
from lib.normalise import (
    WOF_AUS,
    WOF_NZ,
    Geocoder,
    datetime_from_iso_utc,
    html2plain,
)
from lib.salary import get_salary_data
from sources.abstract_datasource import module_name
from sources.commoncrawl_datasource import CommonCrawlDatasource


def fixup_careers_vic_location(loc):
    loc = re.sub("(.*)/(.*)", r"\1 \2", loc)
    return re.sub(r"(.*)\|(.*)", r"\2, \1, Victoria, Australia", loc)


# CAREERS_VIC_MAPPINGS = {
#     'Location: ': 'jobLocation', # name?
#     'Job type: ': 'employmentType',
#     'Organisation: ': 'hiringOrganization',
#     'Salary: ': 'baseSalary',
#     'Occupation: ': 'industry',
#     'Reference: ': 'identifier',
#     'Job posted: ': 'datePosted',
#     'Closes: ': 'validThrough',
#     'Classification: ': 'occupationalCategory',
#     'Contact: ': 'applicationContact',
# }
# #
# CAREERS_VIC_IGNORE = [
#     'Salary Range: ', # Same as Salary?
#     'Work location: ', # Same as Location?
#     'Job duration: ', # End date of job. Part of employmenType???
# ]


AU_GEOCODER = Geocoder(lang="en", filter_country_ids=(WOF_AUS, WOF_NZ))


class Datasource(CommonCrawlDatasource):

    name = module_name(__name__)
    query = "careers.vic.gov.au/job/*"

    def extract(self, html: Union[bytes, str], uri, view_date) -> List[Dict[Any, Any]]:
        soup = bs4.BeautifulSoup(html, "html5lib")
        data = {}
        for info in soup.select(".txt-info"):
            key = info.select_one(".txt-bold")
            if not key:
                continue
            key_text = key.get_text().strip()
            value = "".join(str(s).strip() for s in key.next_siblings)
            data[key_text] = value

            title_tag = soup.select_one(".txt-title")
            if not title_tag:
                logging.warning("Missing title tag in %s", uri)
                title = None
            else:
                title = str(title_tag.get_text())
            description = str(soup.select_one(".txt-pre-line") or "")
        return [
            {
                "title": title,
                "description": description,
                "metadata": data,
                "uri": uri,
                "view_date": view_date,
            }
        ]

    def normalise(self, title, description, metadata, uri, view_date):
        salary_data = get_salary_data(
            metadata.get("Salary:") or metadata["Salary Range:"]
        )
        location_raw = metadata.get("Location:") or metadata["Work location:"]
        return {
            "title": title,
            "description": html2plain(description),
            "uri": uri,
            "view_date": datetime_from_iso_utc(view_date),
            "org": metadata.get("Organisation:"),
            **salary_data,
            "location_raw": location_raw,
            **AU_GEOCODER.geocode(fixup_careers_vic_location(location_raw)),
        }
