import re
from enum import IntEnum
from typing import Dict, List, Optional, Set, Tuple, TypedDict

SalaryRange = Tuple[float, float]

MAX_SALARY_RANGE_FRAC = 1.5


class Period(IntEnum):
    HOUR = 1
    DAY = 8
    WEEK = 40
    YEAR = 2000


def valid_salary_period(
    salary: float,
    period: Period,
    period_salary_range: Dict[Period, SalaryRange],
) -> bool:
    """Is salary within period_salary_range for period"""
    min_salary, max_salary = period_salary_range[period]
    return min_salary <= salary <= max_salary


def infer_salary_hours(
    salary: float,
    period_salary_range: Dict[Period, SalaryRange],
    allowed_periods: Optional[Set[Period]] = None,
) -> Optional[Period]:
    """Returns allowed_period with salary in period_salary_range if unique

    If there are multiple possible periods that the salary falls into the range of,
    or if there are no possible periods then returns None.
    """
    if allowed_periods is None:
        allowed_periods = set(period_salary_range.keys())
    possible_periods = [
        period
        for period in allowed_periods
        if valid_salary_period(salary, period, period_salary_range)
    ]
    if len(possible_periods) == 1:
        return possible_periods[0]
    # Ambiguous or no match
    return None


def salary_range_frac(min_salary: float, max_salary: float) -> float:
    """Returns the fraction of the salary range relative to the midpoint

    For example since (75, 125) are 100 +/- 25, and (2*25)/100 = 0.5
        salary_range_frac(75, 125) == 0.5
    """
    avg_salary = (max_salary + min_salary) / 2.0
    return (max_salary - min_salary) / avg_salary


def valid_salary_range(
    min_salary: float,
    max_salary: float,
    max_salary_range_frac: float = MAX_SALARY_RANGE_FRAC,
) -> bool:
    """Returns whether the range min_salary to max_salary is valid

    Checks whether they are ordered correctly and within max_salary_range_frac.
    """
    if max_salary < min_salary:
        return False
    if salary_range_frac(min_salary, max_salary) > max_salary_range_frac:
        return False
    return True


def salary_unit(text: str) -> Optional[Period]:
    """Extracts the salary Period from the text"""
    if re.search(r"(?i)(\b|\d)(year|yearly|annual|annum|p[./]?a)\b", text):
        return Period.YEAR
    if re.search(r"(?i)(\b|\d)(p?/\s*hr?|hour|hourly|p\.?hr?)\b", text):
        return Period.HOUR
    if re.search(r"(?i)(\b|\d)(p?/\s*d|day|daily|diem|p\.?d)\b", text):
        return Period.DAY
    if re.search(r"(?i)(\b|\d)(p?/\s*w|week|weekly|p\.?w)\b", text):
        return Period.WEEK
    return None


# http://jkorpela.fi/dashes.html
HYPHEN = "[-~\u00ad\u2010\u2011\u2012\u2013\u2014\u2015\u2053\u207b\u208b\u2212\ufe58\ufe63\uff0d_]"

BLACKLIST = ["days", "day", "nights", "night", "%", "am", "a.m", "pm", "p.m", "a m"]
BLACKLIST_RE = "(?:" + "|".join(BLACKLIST) + ")"
NUMBER_RE = fr"""(?:[A-Z][A-Z][A-Z]?)?([\$£€]?\s*\d[\d\s,]*(?:[kK]|\.[\d\s]+)?\s*{BLACKLIST_RE}?)"""
RANGE_RE = fr"""{NUMBER_RE}\s*(?:{HYPHEN}|to)\s*{NUMBER_RE}"""


def invalid_number(number: str) -> bool:
    return any(term in number.lower() for term in BLACKLIST)


def parse_number(number: str) -> float:
    number = number.strip(",.$£€").strip()
    number = re.sub(r"[\s,]", "", number)
    number = number.lower().replace("k", "000")
    return float(number)


def is_year(number: float) -> bool:
    return 1900 < number < 2050


def fix_salary_scale(low: float, high: float) -> Tuple[float, float]:
    if low * 1000 < high < low * 2000:
        return low * 1000, high
    else:
        return low, high


def extract_salary(text: str) -> Tuple[Optional[float], Optional[float]]:
    """Returns the salary range (min, max) from the text

    If there is only a single salary then returns None for max
      extract_salary("$55 - $65 per hour") == (55, 65)
      extract_salary("$40.01 ph") == (40.01, None)
    """
    range_matches: List[Tuple[str, str]] = [
        (low, high)
        for low, high in re.findall(RANGE_RE, text, flags=re.IGNORECASE)
        if not invalid_number(low) and not invalid_number(high)
    ]
    # Try to find a dollar
    for low, high in range_matches:
        if "$" in low or "$" in high:
            return fix_salary_scale(parse_number(low), parse_number(high))
    if range_matches:
        low, high = range_matches[0]
        return fix_salary_scale(parse_number(low), parse_number(high))
    matches: List[str] = [
        match
        for match in re.findall(r"(?:\s|^)" + NUMBER_RE, text, flags=re.IGNORECASE)
        if not invalid_number(match)
    ]
    for match in matches:
        if "$" in match:
            return parse_number(match), None
    if matches:
        match = matches[0]
        ans = parse_number(match)
        if not is_year(ans):
            return ans, None
    return (None, None)


class SalaryData(TypedDict):
    salary_raw: str
    salary_min: Optional[float]
    salary_max: Optional[float]
    salary_hours: Optional[Period]


def get_salary_data(salary_raw: Optional[str]) -> SalaryData:
    """Return dictionary of extracted salary data

    If None is passed returns an empty salary data"""
    salary_raw = salary_raw or ""
    salary_min, salary_max = extract_salary(salary_raw)
    salary_hours = salary_unit(salary_raw)
    return {
        "salary_raw": salary_raw,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_hours": salary_hours,
    }
