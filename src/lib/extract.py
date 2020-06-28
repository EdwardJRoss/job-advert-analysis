import logging
from typing import Dict, Any
import demjson

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
    return data

def parse_js_redux(text):
    return parse_js_obj(text, JS_STR_REDUX)

