#!/usr/bin/env bash
set -euo pipefail

black -t py36 job_pipeline/
python -m isort -m 3 --trailing-comma job_pipeline/
