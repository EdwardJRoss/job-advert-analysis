#!/bin/bash
set -exuo pipefail
# Downloads and unpacks all the source files from Kaggle
# Requires Kaggle API to be configued: https://github.com/Kaggle/kaggle-api
# And Competition Rules to be Accepted: https://www.kaggle.com/c/job-salary-prediction/data
# Will results in data/01_raw/{Test/Train/Valid}_rev1.csv
dest=../data/01_raw

mkdir -p "$dest"

for file in Test_rev1.zip Train_rev1.zip Valid_rev1.csv; do
    kaggle competitions download -c job-salary-prediction --path "$dest" -f "$file"
done

find "$dest" -name '*.zip' -execdir unzip '{}' ';'
find "$dest" -name '*.zip' -exec rm '{}' ';'
