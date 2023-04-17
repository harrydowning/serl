#! /usr/bin/bash

pip install .
pytest -s -v --cov --cov-report term tests
rm .coverage
