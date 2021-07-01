import json
import logging
from typing import Any, Dict, Optional

import demjson


class ParseError(Exception):
    pass


def extract_braces(text: str) -> str:
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
        if char == "\\":
            escape = True
        if (not inquote) and char == "{":
            if start is None:
                start = idx
            depth += 1
        if (not inquote) and char == "}":
            if start is None:
                raise ParseError("Unexpected close brace")
            depth -= 1
            if depth <= 0:
                break
    else:
        raise ParseError("Unexpected end of stream")
    return text[start : idx + 1]


def parse_js_obj(text: str, init: str) -> Optional[Dict[Any, Any]]:
    idx = text.find(init)
    if idx < 0:
        return None
    try:
        match_text = extract_braces(text[idx:])
    except ParseError as e:
        logging.warning("Error parsing object: %s", e)
        return None
    try:
        # 20x faster
        data = json.loads(match_text)
    except json.decoder.JSONDecodeError:
        logging.debug("Defaulting to demjson")
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
