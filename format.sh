#!/usr/bin/env bash
set -euo pipefail

black -t py36 src/ tests/
python -m isort -m 3 --trailing-comma src/ tests/
