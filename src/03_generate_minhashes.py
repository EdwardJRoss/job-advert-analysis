#!/usr/bin/env python
import pickle
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from lib.nlp import tokenize, minhash, shingle

SHINGLE_LENGTH = 7
NUM_PERM = 128

INPUT = Path('../data/02_primary/ads.feather')
OUTPUT = Path('../data/03_features/minhash.pkl')

OUTPUT.parent.mkdir(exist_ok=True)


df = (pd
      .read_feather(INPUT, columns=['Id', 'FullDescription'])
      .set_index('Id')
      )

# Transforms: Tokenize
# Then shingle to shingle length
minhashes = {idx: minhash(shingle(tokenize(row['FullDescription']), SHINGLE_LENGTH),
                          num_perm=NUM_PERM)
             for idx, row in tqdm(df.iterrows(), total=len(df))}

output = {'num_perm': NUM_PERM,
          'minhashes': minhashes}

with open(OUTPUT, 'wb') as f:
    pickle.dump(output, f)
