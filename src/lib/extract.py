import logging
from typing import Dict, Any, Generator, Union
import json
import demjson
from warcio.recordloader import ArcWarcRecord
import extruct
import bs4

# TODO: datatype should be enum/list?
def parse_warc(warc: ArcWarcRecord, parser: str) -> Generator[Dict[Any, Any], None, None]:
    html = warc.content_stream().read()
    uri = warc.rec_headers['WARC-Target-URI']
    date = warc.rec_headers['WARC-Date']
    assert uri is not None
    assert date is not None

    if parser == 'jsonld':
        data = parse_jsonld(html, uri)
    elif parser == 'microdata':
        data = parse_microdata(html, uri)
    elif parser == 'careers_vic':
        data = [parse_careers_vic(html)]
    elif parser == 'iworkfornsw':
        data = [parse_iworkfornsw(html)]
    elif parser == 'probono':
        data = [parse_probono(html)]
    elif parser == 'sk':
        data = parse_sk(html)
    elif parser == 'gt':
        data = parse_gt(html)
    else:
        raise ValueError(f'Unkown parser {parser}')

    for datum in data:
        # Is there a better way to encode this?
        datum['_source_uri'] = uri
        datum['_source_date'] = date
        datum['_source'] = 'warc'
        yield datum


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
def parse_careers_vic(html: Union[bytes, str]):
    soup = bs4.BeautifulSoup(html, 'html5lib')
    # Is the second location ever different?
    data = {}
    for info in soup.select('.txt-info'):
        key = info.select_one('.txt-bold')
        key_text = key.get_text()
        if key_text in CAREERS_VIC_IGNORE:
            continue
        jp_key = CAREERS_VIC_MAPPINGS[key_text]
        value = ''.join(str(s).strip() for s in key.next_siblings)
        data[jp_key] = value

    data['title'] = str(soup.select_one('.txt-title').get_text())
    data['description'] = str(soup.select_one('.txt-pre-line'))
    return data

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
def parse_iworkfornsw(html: Union[bytes, str]):
    soup = bs4.BeautifulSoup(html, 'html5lib')
    body = soup.find('tbody')
    infos = body.find_all('tr')
    data = {IWORKFORNSW_MAPPINGS[info.th.get_text().strip()]: info.td.get_text().strip() for info in infos}
    data['title'] = soup.select_one('.job-detail-title').get_text().strip()
    data['description'] = str(soup.select_one('.job-detail-des'))
    return data

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
def parse_probono(html: Union[bytes, str]):
    soup = bs4.BeautifulSoup(html, 'html5lib')
    infos = soup.select_one('.org-basic-info').div.select('p.org-add')
    data = {}
    for info in infos:
        key = info.b
        schema_key = PROBONO_MAPPINGS[key.get_text().strip()]
        value = ''.join(str(s.get_text() if isinstance(s, bs4.element.Tag) else s).strip() for s in key.next_siblings)
        data[schema_key] = value
    data['description'] = str(soup.select_one('#about-role'))
    data['hiringOrganization_description'] = str(soup.select_one('#about-organisation'))
    data['title'] = soup.h1.get_text().strip()
    return data


def parse_jsonld(html: Union[bytes,str], base_url: str) -> Generator[Dict[Any, Any], None, None]:
    data = extruct.extract(html, base_url, syntaxes=['json-ld'])['json-ld']
    job_posts = [datum for datum in data if datum['@type'] == 'JobPosting']
    for post in job_posts:
        yield post

def parse_microdata(html: Union[bytes,str], base_url: str) -> Generator[Dict[Any, Any], None, None]:
    data = extruct.extract(html, base_url, syntaxes=['microdata'])['microdata']
    job_posts = [datum['properties'] for datum in data if datum['type'] == 'http://schema.org/JobPosting']
    for post in job_posts:
        yield post

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

JS_STR_REDUX = 'REDUX_DATA ='
JS_STR_APP = 'window.APP_DATA ='
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

def parse_sk(html: str):
    text = html.decode('utf-8')
    obj = parse_js_obj(text, JS_STR_REDUX)
    if obj is None:
        return []
    else:
        return [obj['jobdetails']['result']]

def parse_gt(html: str):
    text = html.decode('utf-8')
    obj = parse_js_obj(text, JS_STR_APP)
    if obj is None:
        return []
    else:
        data = obj['vip']['item']
        if data['isJobsCategory']:
            return [data]
        else:
            return []

def undefined_to_none(dj):
    if isinstance(dj, dict):
        return {k: undefined_to_none(v) for k, v in dj.items()}
    if isinstance(dj, list):
        return [undefined_to_none(k) for k in dj]
    elif dj == demjson.undefined:
        return None
    else:
        return dj
