#!/bin/bash

. venv/bin/activate
export FLASK_ENV=testing
export FLASK_APP=shhh

printf "*** Running unit tests **************************************\n"
python -m unittest discover -s ./shhh/tests/ -p 'test_*.py' -v
