#!/usr/bin/env bash
set -euo pipefail

# Correctness
python -m pyflakes src/

# Style
python -m isort -m 3 --trailing-comma -c src/
python -m isort -m 3 --trailing-comma -c tests/
black --check -t py36 src/ tests/
cd src
mypy $(find . -name '*.py')
