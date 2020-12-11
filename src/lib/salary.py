import re

HOUR = 1
DAY = 8
WEEK = 40
YEAR = 2000


def salary_unit(text):
    if re.search(r"(?i)(\b|\d)(year|yearly|annual|annum|p[./]?a)\b", text):
        return YEAR
    if re.search(r"(?i)(\b|\d)(p?/\s*hr?|hour|hourly|p\.?hr?)\b", text):
        return HOUR
    if re.search(r"(?i)(\b|\d)(p?/\s*d|day|daily|diem|p\.?d)\b", text):
        return DAY
    if re.search(r"(?i)(\b|\d)(p?/\s*w|week|weekly|p\.?w)\b", text):
        return WEEK


# http://jkorpela.fi/dashes.html
HYPHEN = "[-~\u00ad\u2010\u2011\u2012\u2013\u2014\u2015\u2053\u207b\u208b\u2212\ufe58\ufe63\uff0d]"


def parse_number(number):
    number = number.strip(",.$£€").strip()
    number = re.sub(r"[\s,]", "", number)
    number = number.lower().replace("k", "000")
    return float(number)


NUMBER_RE = r"""(?:[A-Z][A-Z][A-Z]?)?([\$£€]?\s*\d[\d\s,]*(?:[kK]|\.[\d\s]+)?)"""
NOT_PCT_RE = r"""\s*?(?:[^%\d]|$)"""
RANGE_RE = fr"""{NUMBER_RE}\s*(?:{HYPHEN}|to)\s*{NUMBER_RE}{NOT_PCT_RE}"""


def fix_salary_scale(low, high):
    if low * 1000 < high < low * 2000:
        return low * 1000, high
    else:
        return low, high


def extract_salary(text):
    range_matches = re.findall(RANGE_RE, text)
    # Try to find a dollar
    for match in range_matches:
        low, high = match
        if "$" in low or "$" in high:
            return fix_salary_scale(parse_number(low), parse_number(high))
    if range_matches:
        match = range_matches[0]
        low, high = match
        return fix_salary_scale(parse_number(low), parse_number(high))
    matches = re.findall(r"(?:\s|^)" + NUMBER_RE + NOT_PCT_RE, text)
    for match in matches:
        if "$" in match:
            return parse_number(match), None
    if matches:
        match = matches[0]
        return parse_number(match), None
    return (None, None)


def get_salary_data(salary_raw):
    """Return dictionary of extracted salary data"""
    salary_min, salary_max = extract_salary(salary_raw or "")
    salary_hours = salary_unit(salary_raw or "")
    return {
        "salary_raw": salary_raw,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_hours": salary_hours,
    }
