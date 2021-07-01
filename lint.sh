#!/usr/bin/env bash
set -exuo pipefail

# Correctness
python -m pyflakes job_pipeline/

# Style
python -m isort -m 3 --trailing-comma -c job_pipeline/ tests/
MYPYPATH=./typestubs/ mypy job_pipeline
black --check -t py36 job_pipeline/ tests/
