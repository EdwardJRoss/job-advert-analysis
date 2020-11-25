from lib.normalise import WOF_AUS, WOF_NZ, Geocoder, location_jsonld
from sources.jsonld import Datasource as JSONLinkedDatasource

AU_GEOCODER = Geocoder(lang="en", filter_country_ids=(WOF_AUS, WOF_NZ))


class Datasource(JSONLinkedDatasource):
    name = "ethicaljobs"

    def normalise(self, data, uri, view_date):
        ans = super().normalise(data, uri, view_date)
        # Salary not in metadata
        location_raw = location_jsonld(data)
        return {
            **ans,
            "location_raw": location_raw,
            **AU_GEOCODER.geocode(location_raw),
        }
