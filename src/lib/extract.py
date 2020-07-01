import logging
from typing import Dict, Any, Generator, Union
from warcio.recordloader import ArcWarcRecord
import demjson
import extruct

# TODO: datatype should be enum/list?
def parse_warc(warc: ArcWarcRecord, parser: str) -> Generator[Dict[Any, Any], None, None]:
    html = warc.content_stream().read()
    uri = warc.rec_headers['WARC-Target-URI']
    date = warc.rec_headers['WARC-Date']
    assert uri is not None
    assert date is not None

    if parser == 'jsonld':
        data = parse_jsonld(html, uri)
    elif parser == 'js_redux':
        # TODO: Get source encoding? Interpret as bytes?
        result = parse_js_redux(html.decode('utf-8'))
        if result is None:
            data = []
        else:
            data = [result]
    elif parser == 'js_app':
        # TODO: Get source encoding? Interpret as bytes?
        data = parse_js_app(html.decode('utf-8'))
        if result is None:
            data = []
        else:
            data = [result]
    else:
        raise ValueError(f'Unkown datatype {datatype}')

    for datum in data:
        # Is there a better way to encode this?
        datum['_source_uri'] = uri
        datum['_source_date'] = date
        datum['_source'] = 'warc'
        yield datum



def parse_jsonld(html: Union[bytes,str], base_url: str) -> Generator[Dict[Any, Any], None, None]:
    data = extruct.extract(html, base_url, syntaxes=['json-ld'])['json-ld']
    job_posts = [datum for datum in data if datum['@type'] == 'JobPosting']
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
JS_STR_APP = 'window.app_data ='
def parse_js_obj(text: str, init: str) -> Dict[Any, Any]:
    idx = text.find(init)
    if idx < 0:
        return None
    try:
        match_text = extract_braces(text[idx:])
    except ParseError as e:
        logging.warning('Error parsing object: %s', e)
        return None
    data = demjson.decode(match_text)
    data = undefined_to_none(data)
    return data

def parse_js_redux(text: str):
    return parse_js_obj(text, JS_STR_REDUX)

def parse_js_app(text: str):
    return parse_js_obj(text, JS_STR_APP)

def undefined_to_none(dj):
    if isinstance(dj, dict):
        return {k: undefined_to_none(v) for k, v in dj.items()}
    if isinstance(dj, list):
        return [undefined_to_none(k) for k in dj]
    elif dj == demjson.undefined:
        return None
    else:
        return dj
