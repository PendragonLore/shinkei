#!/usr/bin/env bash

PYTHONPATH="$(pwd)" pytest -vs
isort . --check-only --recursive
flake8 .
mypy -p shinkei
pydocstyle shinkei
python ./setup.py sdist bdist_egg bdist_wheel
cd docs && make html