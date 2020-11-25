from lib.extractlib import parse_js_obj
from lib.normalise import (
    WOF_AUS,
    WOF_NZ,
    Geocoder,
    datetime_from_iso_utc,
    html2plain,
)
from lib.salary import get_salary_data

AU_GEOCODER = Geocoder(lang="en", filter_country_ids=(WOF_AUS, WOF_NZ))
JS_STR_REDUX = "REDUX_DATA ="


class Datasource:
    name = "sk"

    def extract(self, html: str, uri, view_date):
        text = html.decode("utf-8")
        obj = parse_js_obj(text, JS_STR_REDUX)
        if obj is None:
            return []
        else:
            return [
                {
                    "data": obj["jobdetails"]["result"],
                    "uri": uri,
                    "view_date": view_date,
                }
            ]

    def normalise(self, data, uri, view_date):
        salary_text = data["salary"]
        location = data["locationHierarchy"]
        location_text = ", ".join(
            [
                location["suburb"],
                location["city"],
                location["state"],
                location["nation"],
            ]
        )
        return {
            "title": data["title"],
            "description": html2plain(data["mobileAdTemplate"]),
            "uri": uri,
            "view_date": datetime_from_iso_utc(view_date),
            "org": data["advertiser"]["description"],
            **get_salary_data(salary_text),
            "location_raw": location_text,
            **AU_GEOCODER.geocode(location_text),
        }
