from lib.normalise import WOF_AUS, WOF_NZ, Geocoder
from sources.microdata import Datasource as MicrodataDatasource

AU_GEOCODER = Geocoder(lang='en', filter_country_ids=(WOF_AUS, WOF_NZ))

class Datasource(MicrodataDatasource):
    name = 'jobs.csiro.au'
    def normalise(self, data, uri, view_date):
        # Description is dometimes a list, e.g. CC-MAIN-2019-18
        if isinstance(data.get('description'), list):
            data['description'] = '\n'.join(data['description'])
        ans = super().normalise(data, uri, view_date)
        # jobLocation *can* be an array
        location_raw = str(data.get('jobLocation') or '')
        return {
            **ans,
            'location_raw': location_raw,
            **AU_GEOCODER.geocode(location_raw),
            }
