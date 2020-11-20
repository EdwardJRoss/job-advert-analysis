import re
from datetime import datetime, timezone
import functools
import requests
from html2text import HTML2Text
from bs4 import BeautifulSoup
import mistletoe

def datetime_from_iso_utc(t):
    d = datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ')
    d = d.astimezone(timezone.utc)
    return d

def html2md(html):
    parser = HTML2Text()
    parser.ignore_images = True
    parser.ignore_anchors = True
    parser.body_width = 0
    md = parser.handle(html)
    return md

def normalise_markdown_lists(md):
    return re.sub(r'(^|\n) ? ? ?\\??[•·\–\-\—\-\*]( \w)', r'\1  *\2', md)

def fixup_markdown_formatting(text):
    # Strip off table formatting
    text = re.sub(r'(^|\n)\|\s*', r'\1', text)
    # Strip off extra emphasis
    text = re.sub(r'\*\*', '', text)
    # Remove trailing whitespace and leading newlines
    text = re.sub(r' *$', '', text)
    text = re.sub(r'\n\n+', r'\n\n', text)
    text = re.sub(r'^\n+', '', text)
    return text

def html2plain(html):
    md = html2md(html)
    md = normalise_markdown_lists(md)
    html_simple = mistletoe.markdown(md)
    text = BeautifulSoup(html_simple, 'html.parser').getText()
    text = fixup_markdown_formatting(text)
    return text

# Who's on First Placenames
WOF_AUS = 85632793
WOF_NZ = 85633345
class Geocoder:
    """Wrapper around Placeholder geocoder"""
    def __init__(self, uri='http://localhost:3000/parser/search', lang=None, filter_country_ids=None):
        self.uri = uri
        self.lang = lang
        self.filter_country_ids = filter_country_ids

    @functools.lru_cache(maxsize=128)
    def geocode(self, loc, lang=None, filter_country_ids=None):
        lang = lang or self.lang
        filter_country_ids = filter_country_ids or self.filter_country_ids
        params = {'text': loc}
        if lang:
            params['lang'] = lang

        r = requests.get(self.uri, params=params)
        r.raise_for_status()
        places = r.json()
        for place in places:
            for l in place['lineage']:
                if (not filter_country_ids) or ('country' in l and l['country']['id'] in filter_country_ids):
                    return {
                        'loc_id': place['id'],
                        **{'loc_' + key: value['name'] for key, value in l.items()},
                    }
        # Fail
        return {}

def location_jsonld(data, default_country='AU'):
    parts = []
    locality = data['jobLocation']['address']['addressLocality']
    if locality:
        # Fixup
        locality_out = re.sub(' C B D$', '', locality)
        parts.append(locality_out)
    region = data['jobLocation']['address']['addressRegion']
    if region and region != locality:
        region_out = re.sub(' C B D$', '', region)
        parts.append(region_out)
    postalCode = data['jobLocation']['address']['postalCode']
    if postalCode:
        parts.append(postalCode)
    country = data['jobLocation']['address']['addressCountry']
    if country:
        parts.append(country)
    elif default_country:
        parts.append(default_country)
    return ', '.join(parts)
