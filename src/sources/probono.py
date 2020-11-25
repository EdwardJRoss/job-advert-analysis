from typing import Union
import bs4
import re
from lib.normalise import Geocoder, WOF_AUS, WOF_NZ, datetime_from_iso_utc, html2plain
from lib.salary import get_salary_data

AU_GEOCODER = Geocoder(lang='en', filter_country_ids=(WOF_AUS, WOF_NZ))

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
    return re.sub(r'(.*)\((.*)\)', '\\2, \\1', loc)

class Datasource():
    name = 'probono'
    def extract(self, html: Union[bytes, str], uri, view_date):
        soup = bs4.BeautifulSoup(html, 'html5lib')
        infos = soup.select_one('.org-basic-info').div.select('p.org-add')
        data = {}
        for info in infos:
            key = info.b
            schema_key = key.get_text().strip()
            value = ''.join(str(s.get_text() if isinstance(s, bs4.element.Tag) else s).strip() for s in key.next_siblings)
            data[schema_key] = value
        description = str(soup.select_one('#about-role'))
        hiringOrganization_description = str(soup.select_one('#about-organisation'))
        title = soup.h1.get_text().strip()
        return [{'title': title, 'description': description, 'organisation_description': hiringOrganization_description, 'metadata': data, 'uri': uri, 'view_date': view_date}]

    def normalise(self, title, description, organisation_description, metadata, uri, view_date):
        salary_text = metadata.get('Salary :')
        salary_data = get_salary_data(salary_text)
        location_raw = metadata['Location :']
        return {
            'title': title,
            'description': html2plain(description),
            'uri': uri,
            'view_date': datetime_from_iso_utc(view_date),
            'org': metadata.get('Organisation :'),
            **salary_data,
            'location_raw': location_raw,
            **AU_GEOCODER.geocode(fix_probono_location(location_raw)),
        }
