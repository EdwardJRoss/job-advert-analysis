import logging
from typing import Dict, Any, Generator, Union, List
import json
import demjson
from warcio.recordloader import ArcWarcRecord
import extruct
import bs4
from lib.normalise import html2plain

HANDLERS = {}

def parse(extract, normalise, html, uri, date):
    return [normalise(**item) for item in extract(html, uri, date)]

# TODO: datatype should be enum/list?
def extract_warc(warc: ArcWarcRecord, parser: str) -> Generator[Dict[str, Any], None, None]:
    html = warc.content_stream().read()
    uri = warc.rec_headers['WARC-Target-URI']
    date = warc.rec_headers['WARC-Date']
    assert uri is not None
    assert date is not None

    data = HANDLERS[parser]['extract'](html, uri, date)

    for datum in data:
        datum['source_uri'] = uri
        datum['source_date'] = date
        datum['source'] = 'warc'
        yield datum

def normalise_warc(data: Dict[str, Any], parser: str):
    normalise = HANDLERS[parser]['normalise']
    # TODO
    del data['source_uri']
    del data['source_date']
    del data['source']
    return normalise(**data)


################################################################################
## Careers Vic
################################################################################

def extract_careers_vic(html: Union[bytes, str], _uri, _date):
    soup = bs4.BeautifulSoup(html, 'html5lib')
    data = {}
    for info in soup.select('.txt-info'):
        key = info.select_one('.txt-bold')
        key_text = key.get_text().strip()
        value = ''.join(str(s).strip() for s in key.next_siblings)
        data[key_text] = value
    
    title = str(soup.select_one('.txt-title').get_text())
    description = str(soup.select_one('.txt-pre-line'))
    return [{'title': title, 'description': description, 'metadata': data}]


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
def normalise_careers_vic(title, description, metadata):
    return {
        'title': title,
        'description': html2plain(description),
    }

HANDLERS['careers_vic'] = {
    'extract': extract_careers_vic,
    'normalise': normalise_careers_vic,
}


################################################################################
## I Work for NSW
################################################################################

def extract_iworkfornsw(html: Union[bytes, str], _uri, _date):
    soup = bs4.BeautifulSoup(html, 'html5lib')
    body = soup.find('tbody')
    infos = body.find_all('tr')
    data = {info.th.get_text().strip(): info.td.get_text().strip() for info in infos}
    title = soup.select_one('.job-detail-title').get_text().strip()
    description = str(soup.select_one('.job-detail-des'))
    return [{'title': title, 'description': description, 'metadata': data}]

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
def normalise_iworkfornsw(title, description, metadata):
    return {
        'title': title,
        'description': html2plain(description),
    }

HANDLERS['iworkfornsw'] = {
    'extract': extract_iworkfornsw,
    'normalise': normalise_iworkfornsw,
}

################################################################################
## Probono
################################################################################

def extract_probono(html: Union[bytes, str], _uri, _date):
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
    return [{'title': title, 'description': description, 'organisation_description': hiringOrganization_description, 'metadata': data}]


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
def normalise_probono(title, description, organisation_description, metadata):
    return {
        'title': title,
        'description': html2plain(description),
    }

HANDLERS['probono'] = {
    'extract': extract_probono,
    'normalise': normalise_probono,
}

################################################################################
## Seek
################################################################################

JS_STR_REDUX = 'REDUX_DATA ='
def extract_sk(html: str, _uri, _date):
    text = html.decode('utf-8')
    obj = parse_js_obj(text, JS_STR_REDUX)
    if obj is None:
        return []
    else:
        return [{'data': obj['jobdetails']['result']}]


def normalise_sk(data):
    return {
        'title': data['title'],
        'description': html2plain(data['mobileAdTemplate']),
        }


HANDLERS['sk'] = {
    'extract': extract_sk,
    'normalise': normalise_sk,
}

################################################################################
## Gumtree
################################################################################

JS_STR_APP = 'window.APP_DATA ='
def extract_gt(html: str, _uri, _date):
    text = html.decode('utf-8')
    obj = parse_js_obj(text, JS_STR_APP)
    if obj is None:
        return []
    else:
        data = obj['vip']['item']
        if data['isJobsCategory']:
            return [{'data': data}]
        else:
            return []

def normalise_gt(data):
    return {
        'title': data['title'],
        'description': html2plain(data['description']),
        }


HANDLERS['gt'] = {
    'extract': extract_gt,
    'normalise': normalise_gt,
}


################################################################################
## Generic Parsers
################################################################################


def extract_jsonld(html: Union[bytes,str], base_url: str, _date) -> Generator[Dict[Any, Any], None, None]:
    data = extruct.extract(html, base_url, syntaxes=['json-ld'])['json-ld']
    job_posts = [datum for datum in data if datum['@type'] == 'JobPosting']
    for post in job_posts:
        yield {'data': post}


def normalise_jsonld(data):
    return {
        'title': data['title'],
        'description': html2plain(data['description']),
        }

HANDLERS['jsonld'] = {
    'extract': extract_jsonld,
    'normalise': normalise_jsonld,
}

def extract_microdata(html: Union[bytes,str], base_url: str, _date) -> Generator[Dict[Any, Any], None, None]:
    data = extruct.extract(html, base_url, syntaxes=['microdata'])['microdata']
    job_posts = [datum['properties'] for datum in data if datum['type'] == 'http://schema.org/JobPosting']
    for post in job_posts:
        yield {'data': post}

def normalise_microdata(data):
    if 'description' in data:
        description = html2plain(data['description'])
    else:
        description = None
    return {
        'title': data['title'],
        'description': description,
        }

HANDLERS['microdata'] = {
    'extract': extract_microdata,
    'normalise': normalise_microdata,
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
