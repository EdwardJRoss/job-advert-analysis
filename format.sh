#!/usr/bin/env bash
set -euo pipefail

python -m isort src/ -m 3 --trailing-comma
python -m isort tests/ -m 3 --trailing-comma
black -t py36 src/ tests/
