#!/usr/bin/env python
import logging
from pathlib import Path
import pickle
import networkx as nx
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

ADS = Path('../data/02_primary/ads.feather')
PAIRS = Path('../data/03_features/duplicate_ids.pkl')
OUTPUT = Path('../data/04_secondary/ads.feather')
OUTPUT.parent.mkdir(exist_ok=True)

logging.info('Reading pairs')
with open(PAIRS, 'rb') as f:
     pairs = pickle.load(f)
logging.info(f'Read {len(pairs)} ads')

logging.info(f'Finding sets')
G = nx.Graph(pairs)
similar_ads = list(nx.connected_components(G))
lengths = [len(c) for c in similar_ads]
total_length = sum((n * (n-1))/2 for n in lengths)
logging.info(f'Found {len(lengths)} ads for a total of {total_length} pairs')

logging.info('Reading ads')
df = pd.read_feather(ADS)
logging.info(f'Read {len(df)} ads')

logging.info('Updating index')
df['uid'] = df['Id']
df = df.set_index('Id')

for group in similar_ads:
    index = min(group)
    df.loc[list(group), 'uid'] = index
df = df.reset_index()

logging.info('Writing output')
df.to_feather(OUTPUT)
logging.info('Done')
