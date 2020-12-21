#!/usr/bin/env bash
set -euo pipefail

# Correctness
python -m pyflakes src/

# Style
python -m isort -m 3 --trailing-comma -c src/ tests/
black --check -t py36 src/ tests/
cd src
mypy $(find . -name '*.py')
