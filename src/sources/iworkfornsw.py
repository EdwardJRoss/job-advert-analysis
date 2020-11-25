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

AU_GEOCODER = Geocoder(lang="en", filter_country_ids=(WOF_AUS, WOF_NZ))


def fixup_iworkfornsw_loc(loc):
    # Normally multiple lines is statewide; take the broad location
    loc = loc.split("\n")[0]
    # Reverse the location; heuristic but generally gets something close to right (the locations are often ambiguous)
    return (
        ", ".join(reversed(loc.replace("-", "/").replace("&", "/").split("/")))
        + ", NSW, AU"
    )


# IWORKFORNSW_MAPPINGS = {
#     'Organisation/Entity:': 'hiringOrganization',
#     'Job Category:': 'industry',
#     'Job Location:': 'jobLocation',
#     'Job Reference Number:': 'identifier',
#     'Work Type:': 'employmentType',
#     'Number of Positions:': 'totalJobOpenings',
#     'Total Remuneration Package:': 'baseSalary', # A little abuse
#     'Contact:': 'applicationContact',
#     'Closing Date:': 'validThrough',
# }


class Datasource:
    name = "iworkfornsw"

    def extract(self, html: Union[bytes, str], uri, view_date):
        soup = bs4.BeautifulSoup(html, "html5lib")
        body = soup.find("tbody")
        # Some pages are missing a body; e.g. CC-MAIN-2018-17
        if not body:
            return []
        infos = body.find_all("tr")
        data = {
            info.th.get_text().strip(): info.td.get_text().strip() for info in infos
        }
        title = soup.select_one(".job-detail-title").get_text().strip()
        description = str(soup.select_one(".job-detail-des"))
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
        salary = get_salary_data(metadata.get("Total Remuneration Package:") or "")
        location_raw = metadata["Job Location:"]
        return {
            "title": title,
            "description": html2plain(description),
            "uri": uri,
            "view_date": datetime_from_iso_utc(view_date),
            "org": metadata["Organisation/Entity:"],
            **salary,
            "location_raw": location_raw,
            **AU_GEOCODER.geocode(fixup_iworkfornsw_loc(location_raw)),
        }
