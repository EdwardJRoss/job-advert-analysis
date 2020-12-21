Enriching and processing data from the [Job Salary Prediction Kaggle Competiton](https://www.kaggle.com/c/job-salary-prediction/data).

This repository looks at methods of aggregating information from the job ad data.
See [the related articles](https://skeptric.com/tags/jobs/) for more information about the techniques used.

# Setup

Requires Python 3.6+.
Install requirements.txt in an appropriate virtual environment:

```python
# Set up a new virtual environment
python -m venv .venv
# Install requirement
python -m pip install -r requirements.txt
# Download SpaCy model
python -m spacy download en_core_web_lg
```



For [downloading the Kaggle data](src/01b_fetch_kaggle_data.py) you will need [Kaggle API credentials](https://github.com/Kaggle/kaggle-api) set up, and accept the [competition rules](https://www.kaggle.com/c/job-salary-prediction/data). 
Alternatively you can manually download and unzip the data from Kaggle directly.


# Runnning

You can run the whole pipeline in the [src](/src) folder by running `./run.sh`, or run each of the numbered steps independently.

!! Placeholder running on port 3000

