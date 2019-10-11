#!/usr/bin/env bash

#quickly createing venv.

for version in  3.{5,6,7}; do

    python$version -m venv .venv-$version

    source ".venv-${version}/bin/activate"
    python --version

    if [[ $(python --version) == "Python 3.5.4" ]]; then
        PIP_NEED_UPGRADE=$(pip --version | grep "9.0.1")
        if [[ -n "$PIP_NEED_UPGRADE" ]]; then
            curl https://bootstrap.pypa.io/get-pip.py | python3
        fi
    fi

    pip install -q --upgrade pip
    pip --version

    # pip install -q -r requirements.txt
    pip install -e .

    deactivate
done
