#!/bin/bash
set -exuo pipefail

./01_fetch_data.py
./02_extract_data.py
./03_normalise_data.py
