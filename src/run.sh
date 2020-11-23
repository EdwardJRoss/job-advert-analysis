#!/bin/bash
set -exuo pipefail

./00_find_sources.py
./01_fetch_data.py
./02_extract_data.py
./03_normalise_data.py
