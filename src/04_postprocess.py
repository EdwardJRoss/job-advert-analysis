#!/usr/bin/env python
import logging
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

from lib.salary import (
    Period,
    SalaryRange,
    infer_salary_hours,
    valid_salary_period,
    valid_salary_range,
)

INPUT = Path("../data/03_secondary/")
OUTPUT = Path("../data/04_processed/data.pkl")


# Bounds on reasonable salary ranges in AUD
AU_PERIOD_SALARY_RANGE: Dict[Period, SalaryRange] = {
    Period.YEAR: (20000, 500000),
    Period.WEEK: (300, 500),
    Period.DAY: (100, 3000),
    Period.HOUR: (15, 300),
}

# Exclude WEEK as is quite rare
AU_INFER_PERIODS = set([Period.YEAR, Period.DAY, Period.HOUR])


def fixup_zero_salary(df):
    """Replace where salary_min is non-positive with salary_max"""
    zero_salary = df.salary_min <= 0
    df["salary_min"] = df["salary_min"].astype("float")
    df.loc[zero_salary, "salary_min"] = df["salary_max"].astype("float")
    df.loc[df["salary_min"] <= 0, "salary_min"] = np.nan
    df.loc[zero_salary, "salary_max"] = np.nan


def valid_salary_range_ignorena(min_salary, max_salary):
    if pd.isna(min_salary) or pd.isna(max_salary):
        return True
    else:
        return valid_salary_range(min_salary, max_salary)


def valid_salary_period_ignorena(salary, period):
    if pd.isna(salary) or pd.isna(period):
        return True
    else:
        return valid_salary_period(salary, period, AU_PERIOD_SALARY_RANGE)


def enrich_salary_valid(df):
    assert "salary_valid" not in df
    has_salary = df.salary_min > 0

    valid_range = df.apply(
        lambda df: valid_salary_range_ignorena(df.salary_min, df.salary_max), axis=1
    )
    valid_period = df.apply(
        lambda df: valid_salary_period_ignorena(df.salary_min, df.salary_hours), axis=1
    )

    df["salary_valid"] = has_salary & valid_range & valid_period


def infer_salary_hours_au(salary):
    if pd.isna(salary):
        return np.nan
    return infer_salary_hours(salary, AU_PERIOD_SALARY_RANGE, AU_INFER_PERIODS)


def enrich_period_inferred(df):
    assert "salary_hours_inferred" not in df

    df["salary_hours_inferred"] = (
        df["salary_min"].apply(infer_salary_hours_au).astype("float")
    )
    df["salary_hours_inferred"] = df.salary_hours.combine_first(
        df.salary_hours_inferred
    )


def enrich_annualised_salary(df):
    assert "salary_annual" not in df

    df["salary_annual"] = df["salary_min"] * Period.YEAR / df["salary_hours_inferred"]
    df.loc[~df.salary_valid, "salary_annual"] = np.nan
    df["salary_annual"] = df["salary_annual"].astype("float")


def main(data_files: List[Path], outfile: Path) -> None:
    df = pd.concat([pd.read_feather(f) for f in data_files], ignore_index=True)

    fixup_zero_salary(df)
    enrich_salary_valid(df)
    enrich_period_inferred(df)
    enrich_annualised_salary(df)

    outfile.parent.mkdir(exist_ok=True)
    df.to_pickle(outfile)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)

    data_files = [path for d in INPUT.glob("*/") for path in d.glob("*.feather")]

    main(data_files, OUTPUT)
