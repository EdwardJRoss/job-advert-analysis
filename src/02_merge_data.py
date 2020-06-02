#!/usr/bin/env python
import pandas as pd
from pathlib import Path

INPUT = Path('../data/01_raw')
OUTPUT = Path('../data/02_primary')

OUTPUT.mkdir(exist_ok=True)

df = pd.concat([pd
                .read_csv(fname)
                .assign(split=fname.name.split('_')[0])
                for fname in INPUT.glob('*.csv')],
                ignore_index=True)

df['Title'] = df['Title'].fillna('')

df.to_feather(OUTPUT / 'ads.feather')
