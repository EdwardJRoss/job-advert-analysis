Enriching and processing data from the [Job Salary Prediction Kaggle Competiton](https://www.kaggle.com/c/job-salary-prediction/data).

This repository looks at methods of aggregating information from the job ad data.
See [the related articles](https://skeptric.com/tags/jobs/) for more information about the techniques used.

# Setup

Requires Python 3.6+.
Install requirements.txt in an appropriate virtual environment:

```sh
# Set up a new virtual environment
python -m venv --prompt job-advert-analysis .venv
source .venv/bin/activate
# Install requirement
python -m pip install -r requirements.txt
# Download SpaCy model
python -m spacy download en_core_web_lg
```



For downloading the Kaggle data you will need [Kaggle API credentials](https://github.com/Kaggle/kaggle-api) set up, and accept the [competition rules](https://www.kaggle.com/c/job-salary-prediction/data).
Alternatively you can manually download and unzip the data from Kaggle directly.
If you do not wish to use Kaggle datasources then remove them from `DATASOURCES` in `01_fetch_data.py`.


# Runnning

You can run the whole pipeline in the [src](/src) folder by running `./run.sh`, or run each of the numbered steps independently.

You need a [Placeholder](https://github.com/pelias/placeholder) server running on Port 3000 of localhost for locatino normalisation.
Follow [these instructions](https://geocode.earth/blog/2019/almost-one-line-coarse-geocoding) for a simple way to do this using Docker.
