#!/usr/bin/env bash

set -e

_init_env() {
  source env/bin/activate 2>/dev/null ||
    {
      printf "Creating virtual env...\n"
      python -m venv env
      source env/bin/activate
      printf "Installing packages...\n"
      pip install -r requirements.txt >/dev/null 2>&1
    }
}

[[ $VIRTUAL_ENV == "" ]] && _init_env
if [[ -z $TRAVIS ]]; then
  python -m unittest discover -s "./tests" -p 'test_*.py' -v
else
  pip install codecov
  coverage run -m unittest discover
fi
