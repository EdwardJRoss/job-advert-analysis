import logging
from typing import Dict, Any, Generator, Union, List
import json
import demjson
from warcio.recordloader import ArcWarcRecord
import extruct
import bs4
import re
from lib.normalise import html2plain, datetime_from_iso_utc, Geocoder, WOF_AUS, WOF_NZ, location_jsonld
from lib.salary import get_salary_data

# TODO: Check geocoder is accessible
AU_GEOCODER = Geocoder(lang='en', filter_country_ids=(WOF_AUS, WOF_NZ))

HANDLERS = {}

# TODO: datatype should be enum/list?
def extract_warc(warc: ArcWarcRecord, parser: str) -> Generator[Dict[str, Any], None, None]:
    html = warc.content_stream().read()
    uri = warc.rec_headers['WARC-Target-URI']
    view_date = warc.rec_headers['WARC-Date']
    assert uri is not None
    assert view_date is not None

    data = HANDLERS[parser]['extract'](html, uri, view_date)

    for datum in data:
        yield datum

def normalise_warc(data: Dict[str, Any], parser: str):
    normalise = HANDLERS[parser]['normalise']
    return normalise(**data)


################################################################################
## Careers Vic
################################################################################

def extract_careers_vic(html: Union[bytes, str], uri, view_date):
    soup = bs4.BeautifulSoup(html, 'html5lib')
    data = {}
    for info in soup.select('.txt-info'):
        key = info.select_one('.txt-bold')
        key_text = key.get_text().strip()
        value = ''.join(str(s).strip() for s in key.next_siblings)
        data[key_text] = value
    
    title = str(soup.select_one('.txt-title').get_text())
    description = str(soup.select_one('.txt-pre-line'))
    return [{'title': title, 'description': description, 'metadata': data, 'uri': uri, 'view_date': view_date}]


CAREERS_VIC_MAPPINGS = {
    'Location: ': 'jobLocation', # name?
    'Job type: ': 'employmentType',
    'Organisation: ': 'hiringOrganization',
    'Salary: ': 'baseSalary',
    'Occupation: ': 'industry',
    'Reference: ': 'identifier',
    'Job posted: ': 'datePosted',
    'Closes: ': 'validThrough',
    'Classification: ': 'occupationalCategory',
    'Contact: ': 'applicationContact',
}
#
CAREERS_VIC_IGNORE = [
    'Salary Range: ', # Same as Salary?
    'Work location: ', # Same as Location?
    'Job duration: ', # End date of job. Part of employmenType???
]
def normalise_careers_vic(title, description, metadata, uri, view_date):
    salary_data = get_salary_data(metadata['Salary:'])
    location_raw = metadata['Location:']
    return {
        'title': title,
        'description': html2plain(description),
        'uri': uri,
        'view_date': datetime_from_iso_utc(view_date),
        'org': metadata['Organisation:'],
        **salary_data,
        'location_raw': location_raw,
        **AU_GEOCODER.geocode(location_raw),
    }

HANDLERS['careers_vic'] = {
    'extract': extract_careers_vic,
    'normalise': normalise_careers_vic,
}


################################################################################
## I Work for NSW
################################################################################

def extract_iworkfornsw(html: Union[bytes, str], uri, view_date):
    soup = bs4.BeautifulSoup(html, 'html5lib')
    body = soup.find('tbody')
    infos = body.find_all('tr')
    data = {info.th.get_text().strip(): info.td.get_text().strip() for info in infos}
    title = soup.select_one('.job-detail-title').get_text().strip()
    description = str(soup.select_one('.job-detail-des'))
    return [{'title': title, 'description': description, 'metadata': data, 'uri': uri, 'view_date': view_date}]

IWORKFORNSW_MAPPINGS = {
    'Organisation/Entity:': 'hiringOrganization',
    'Job Category:': 'industry',
    'Job Location:': 'jobLocation',
    'Job Reference Number:': 'identifier',
    'Work Type:': 'employmentType',
    'Number of Positions:': 'totalJobOpenings',
    'Total Remuneration Package:': 'baseSalary', # A little abuse
    'Contact:': 'applicationContact',
    'Closing Date:': 'validThrough',
}
def normalise_iworkfornsw(title, description, metadata, uri, view_date):
    salary = get_salary_data(metadata['Total Remuneration Package:'])
    location_raw = metadata['Job Location:']
    return {
        'title': title,
        'description': html2plain(description),
        'uri': uri,
        'view_date': datetime_from_iso_utc(view_date),
        'org': metadata['Organisation/Entity:'],
        **salary,
        'location_raw': location_raw,
        **AU_GEOCODER.geocode(location_raw.replace('\n', ' ')),
    }

HANDLERS['iworkfornsw'] = {
    'extract': extract_iworkfornsw,
    'normalise': normalise_iworkfornsw,
}

################################################################################
## Probono
################################################################################

def extract_probono(html: Union[bytes, str], uri, view_date):
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

def fix_probono_location(loc):
    return re.sub(r'(.*)\((.*)\)', '\\2, \\1', loc)

PROBONO_MAPPINGS = {
    'Organisation :': 'hiringOrganization',
    'Location :': 'jobLocation',
    'Sector :': 'industry',
    'Salary type :': 'baseSalary_unit', # TODO ??
    'Work type :': 'employmentType',
    'Profession :': 'occupationalCategory',
    'Salary :': 'baseSalary',
    'Application closing date :': 'validThrough',
}
def normalise_probono(title, description, organisation_description, metadata, uri, view_date):
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

HANDLERS['probono'] = {
    'extract': extract_probono,
    'normalise': normalise_probono,
}

################################################################################
## Seek
################################################################################

JS_STR_REDUX = 'REDUX_DATA ='
def extract_sk(html: str, uri, view_date):
    text = html.decode('utf-8')
    obj = parse_js_obj(text, JS_STR_REDUX)
    if obj is None:
        return []
    else:
        return [{'data': obj['jobdetails']['result'], 'uri': uri, 'view_date': view_date}]


def normalise_sk(data, uri, view_date):
    salary_text = data['salary']
    location = data['locationHierarchy']
    location_text = ', '.join([location['suburb'], location['city'], location['state'], location['nation']])
    return {
        'title': data['title'],
        'description': html2plain(data['mobileAdTemplate']),
        'uri': uri,
        'view_date': datetime_from_iso_utc(view_date),
        'org': data['advertiser']['description'],
        **get_salary_data(salary_text),
        'location_raw': location_text,
        **AU_GEOCODER.geocode(location_text),
        }


HANDLERS['sk'] = {
    'extract': extract_sk,
    'normalise': normalise_sk,
}

################################################################################
## Gumtree
################################################################################

JS_STR_APP = 'window.APP_DATA ='
def extract_gt(html: str, uri, view_date):
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

def normalise_gt(data, uri, view_date):
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


HANDLERS['gt'] = {
    'extract': extract_gt,
    'normalise': normalise_gt,
}


################################################################################
## Generic Parsers
################################################################################


def extract_jsonld(html: Union[bytes,str], base_url: str, view_date) -> Generator[Dict[Any, Any], None, None]:
    data = extruct.extract(html, base_url, syntaxes=['json-ld'])['json-ld']
    job_posts = [datum for datum in data if datum['@type'] == 'JobPosting']
    for post in job_posts:
        yield {'data': post, 'uri': base_url, 'view_date': view_date}


def normalise_jsonld(data, uri, view_date):
    return {
        'title': data['title'],
        'description': html2plain(data['description']),
        'uri': uri,
        'view_date': datetime_from_iso_utc(view_date),
        'org': data['hiringOrganization']['name'],
        }

def normalise_cgcrecruitment(data, uri, view_date):
    ans = normalise_jsonld(data, uri, view_date)
    salary_raw = data['baseSalary']['value'].get('value')
    salary = get_salary_data(salary_raw)
    location_raw = location_jsonld(data)
    return {
        **ans,
        **salary,
        'location_raw': location_raw,
        **AU_GEOCODER.geocode(location_raw),
    }

def normalise_davidsonwp(data, uri, view_date):
    ans = normalise_jsonld(data, uri, view_date)
    salary_raw = data['baseSalary']['value'].get('value')
    salary = get_salary_data(salary_raw)
    location_raw = location_jsonld(data)
    return {
        **ans,
        **salary,
        'location_raw': location_raw,
        **AU_GEOCODER.geocode(location_raw),
    }

def normalise_engineeringjobs(data, uri, view_date):
    ans = normalise_jsonld(data, uri, view_date)
    salary_raw = data['baseSalary']['value'].get('value')
    salary = get_salary_data(salary_raw)
    location_raw = location_jsonld(data)
    return {
        **ans,
        **salary,
        'location_raw': location_raw,
        **AU_GEOCODER.geocode(location_raw),
    }

def normalise_launchrecruitment(data, uri, view_date):
    ans = normalise_jsonld(data, uri, view_date)
    salary_raw = data['baseSalary']['value'].get('value')
    salary = get_salary_data(salary_raw)
    location_raw = location_jsonld(data)
    return {
        **ans,
        **salary,
        'location_raw': location_raw,
        **AU_GEOCODER.geocode(location_raw),
    }


def normalise_ethicaljobs(data, uri, view_date):
    ans = normalise_jsonld(data, uri, view_date)
    # Salary not in metadata
    location_raw = data['jobLocation']['address']
    return {
        **ans,
        'location_raw': location_raw,
        **AU_GEOCODER.geocode(location_raw),
    }

HANDLERS['jsonld'] = {
    'extract': extract_jsonld,
    'normalise': normalise_jsonld,
}

HANDLERS['davidsonwp'] = {
    'extract': extract_jsonld,
    'normalise': normalise_davidsonwp,
}

HANDLERS['cgcrecruitment'] = {
    'extract': extract_jsonld,
    'normalise': normalise_cgcrecruitment,
}

HANDLERS['launchrecruitment'] = {
    'extract': extract_jsonld,
    'normalise': normalise_launchrecruitment,
}

HANDLERS['ethicaljobs'] = {
    'extract': extract_jsonld,
    'normalise': normalise_ethicaljobs,
}

HANDLERS['engineeringjobs'] = {
    'extract': extract_jsonld,
    'normalise': normalise_engineeringjobs,
}

def extract_microdata(html: Union[bytes,str], base_url: str, view_date) -> Generator[Dict[Any, Any], None, None]:
    data = extruct.extract(html, base_url, syntaxes=['microdata'])['microdata']
    job_posts = [datum['properties'] for datum in data if datum['type'] == 'http://schema.org/JobPosting']
    for post in job_posts:
        yield {'data': post, 'uri': base_url, 'view_date': view_date}

def normalise_microdata(data, uri, view_date):
    if 'description' in data:
        description = html2plain(data['description'])
    else:
        description = None
    return {
        'title': data['title'],
        'description': description,
        'uri': uri,
        'view_date': datetime_from_iso_utc(view_date),
        'org': data.get('hiringOrganization'),
        }

def normalise_csiro(data, uri, view_date):
    ans = normalise_microdata(data, uri, view_date)
    # jobLocation *can* be an array
    location_raw = str(data.get('jobLocation') or '')
    return {
        **ans,
        'location_raw': location_raw,
        **AU_GEOCODER.geocode(location_raw),
        }

HANDLERS['microdata'] = {
    'extract': extract_microdata,
    'normalise': normalise_microdata,
}

HANDLERS['jobs.csiro.au'] = {
    'extract': extract_microdata,
    'normalise': normalise_csiro,
}

################################################################################
## Helper functions
################################################################################

class ParseError(Exception):
    pass

def extract_braces(text):
    depth = 0
    inquote = False
    escape = False
    start = None
    for idx, char in enumerate(text):
        if escape:
            escape = False
            continue
        if char == '"':
            if start is None:
                raise ParseError("Unexpected quote")
            inquote = not inquote
        if char == '\\':
            escape = True
        if (not inquote) and char == '{':
            if start is None:
                start = idx
            depth += 1
        if (not inquote) and char == '}':
            if start is None:
                raise ParseError("Unexpected close brace")
            depth -= 1
            if depth <= 0:
                break
    else:
        raise ParseError("Unexpected end of stream")
    return text[start:idx+1]

def parse_js_obj(text: str, init: str) -> Dict[Any, Any]:
    idx = text.find(init)
    if idx < 0:
        return None
    try:
        match_text = extract_braces(text[idx:])
    except ParseError as e:
        logging.warning('Error parsing object: %s', e)
        return None
    try:
        # 20x faster
        data = json.loads(match_text)
    except json.decoder.JSONDecodeError:
        logging.debug('Defaulting to demjson')
        data = demjson.decode(match_text)
        data = undefined_to_none(data)
    return data


def undefined_to_none(dj):
    if isinstance(dj, dict):
        return {k: undefined_to_none(v) for k, v in dj.items()}
    if isinstance(dj, list):
        return [undefined_to_none(k) for k in dj]
    elif dj == demjson.undefined:
        return None
    else:
        return dj
