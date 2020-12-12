#!/usr/bin/env bash
set -euo pipefail

black -t py36 src/ tests/
find src/ -name *.py -exec python -m isort -m 3 --trailing-comma {} \;
find tests/ -name *.py -exec python -m isort -m 3 --trailing-comma {} \;
