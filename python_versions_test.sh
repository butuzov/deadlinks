#!/usr/bin/env bash


for version in  3.{5,6,7}; do

    python$version -m venv .venv-$version

    source $(pwd)/.venv-$version/bin/activate
    python --version

    # pip  problem
    # curl https://bootstrap.pypa.io/get-pip.py | python3

    if [[ $(python --version) == "Python 3.5.4" ]]; then
        pip --version
        # curl https://bootstrap.pypa.io/get-pip.py | python3
    else
        pip --version
        # pip install -q --upgrade pip
    fi


    pip install -q -r requirements.txt
    pip install -e .

    make mypy

    deactivate
done
