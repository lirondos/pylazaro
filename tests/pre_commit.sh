#!/usr/bin/env bash
set -euxo pipefail

find . -type f -exec dos2unix {} \;

files=(pylazaro/ tests/ setup.py)
isort -rc "${files[@]}"
black "${files[@]}"
flake8 "${files[@]}"
mypy "${files[@]}"
pytest --cov-report term-missing --cov=pylazaro tests/