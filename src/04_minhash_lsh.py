#!/usr/bin/env python
import pickle
import logging
from pathlib import Path
import pandas as pd
from lib.nlp import lsh_similar, relevance

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

NUM_BAND = 42
NUM_ROW = 3
SHINGLE_LENGTH = 7
CUTOFF = 0.7

INPUT = Path('../data/03_features/minhash.pkl')
ADS = Path('../data/02_primary/ads.feather')
OUTPUT = Path('../data/03_features/duplicate_ids.pkl')

logging.info('Loading pickle')
with open(INPUT, 'rb') as f:
     data = pickle.load(f)


logging.info('Loading ads')
df = pd.read_feather(ADS, columns=['Id', 'FullDescription'])

logging.info('Destructuring ads')
ads = dict(zip(df['Id'], df['FullDescription']))
logging.info('Done')
del df
      
similar_pairs = lsh_similar(data['minhashes'], data['num_perm'],
                            bands=NUM_BAND, rows=NUM_ROW)

logging.info('Finding similar pairs')
pairs = [(i, j) for i, j in similar_pairs if
         relevance(ads[i], ads[j], SHINGLE_LENGTH) > CUTOFF]

logging.info('Writing %s pairs', len(pairs))
with open(OUTPUT, 'wb') as f:
     pickle.dump(pairs, f)
