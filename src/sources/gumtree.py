from lib.extractlib import parse_js_obj
from lib.normalise import (WOF_AUS, WOF_NZ, Geocoder, datetime_from_iso_utc,
                           html2plain)
from lib.salary import get_salary_data

AU_GEOCODER = Geocoder(lang='en', filter_country_ids=(WOF_AUS, WOF_NZ))

JS_STR_APP = 'window.APP_DATA ='

class Datasource():
    name = 'gt'
    def extract(self, html: str, uri, view_date):
        text = html.decode('utf-8')
        obj = parse_js_obj(text, JS_STR_APP)
        if obj is None:
            return []
        else:
            data = obj['vip']['item']
            # adType: OFFER is job ad, WANTED is ask for work
            if data['isJobsCategory'] and data['adType'] == 'OFFER':
                return [{'data': data, 'uri': uri, 'view_date': view_date}]
            else:
                return []

    def normalise(self, data, uri, view_date):
        metadata = {row['value']: row['name'] for row in data['mainAttributes']}
        salary_raw = metadata.get('Salary Detail')
        salary_data = get_salary_data(salary_raw)
        return {
            'title': data['title'],
            'description': html2plain(data['description']),
            'uri': uri,
            'view_date': datetime_from_iso_utc(view_date),
            'org': None,
            **salary_data,
            'location_raw': data['mapAddress'],
            **AU_GEOCODER.geocode(data['mapAddress']),
            }
