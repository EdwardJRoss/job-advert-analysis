#!/bin/bash
set -exuo pipefail

./01_fetch_data.sh
./02_merge_data.py
./03_generate_minhashes.py
./04_minhash_lsh.py
./05_minhash_complete.py
