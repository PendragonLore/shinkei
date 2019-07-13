#!/usr/bin/env bash

printf " [32;1m$ pytest [0;m\n"
PYTHONPATH="$(pwd)" pytest -vs
printf " [32;1m$ isort [0;m\n"
isort . --check-only --recursive
printf " [32;1m$ flake8 [0;m\n"
flake8 .
printf " [32;1m$ mypy [0;m\n"
mypy -p shinkei
printf " [32;1m$ pydocstyle [0;m\n"
pydocstyle shinkei

python ./setup.py sdist bdist_egg bdist_wheel

cd docs && make html