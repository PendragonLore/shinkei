#!/usr/bin/env bash

echo -e " [32;1m$ pytest [0;m"
PYTHONPATH="$(pwd)" pytest -vs
echo -e " [32;1m$ isort [0;m"
isort . --check-only --recursive
echo -e " [32;1m$ flake8 [0;m"
flake8 .
echo -e " [32;1m$ mypy [0;m"
mypy -p shinkei
echo -e " [32;1m$ pydocstyle [0;m"
pydocstyle shinkei

python ./setup.py sdist bdist_egg bdist_wheel

cd docs && make html