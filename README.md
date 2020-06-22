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

For [downloading the data](src/01_fetch_data.sh) you will need [Kaggle API credentials](https://github.com/Kaggle/kaggle-api) set up, and accept the [competition rules](https://www.kaggle.com/c/job-salary-prediction/data). 
This script requires a *nix system with bash, find and unzip; Windows users can use [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10) or [Cygwin](https://www.cygwin.com/)).
Alternatively you can manually [download](https://www.kaggle.com/c/job-salary-prediction/data) and unzip the data from Kaggle directly.
Note that by the competition rules:

> Participants may only use the data for participation in the competition or for academic research purposes (crediting Adzuna), under no circumstances can this data be distributed or used for other commercial purposes.

This repository is essentially academic research; thanks Adzuna!

# Runnning

You can run the whole pipeline in the [src](/src) folder by running `./run.sh`, or run each of the numbered steps independently.
The whole process takes about 1.5 hours on my machine.

# Todo

Can we add new data sources like https://www.kaggle.com/PromptCloudHQ/usbased-jobs-from-dicecom and https://www.kaggle.com/PromptCloudHQ/us-jobs-on-monstercom?

Can we get any other sources of job ads?