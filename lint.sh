#!/usr/bin/env bash
set -euo pipefail

# Correctness
python -m pyflakes src/

# Style
python -m isort -m 3 -tc -c
black --check -t py36 src/
