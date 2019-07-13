#!/usr/bin/env bash

echo "$ pytest"
PYTHONPATH="$(pwd)" pytest -vs
echo "$ isort"
isort . --check-only --recursive
echo "$ flake8"
flake8 .
echo "$ mypy"
mypy -p shinkei
echo "$ pydocstyle"
pydocstyle shinkei

python ./setup.py sdist bdist_egg bdist_wheel

cd docs && make html