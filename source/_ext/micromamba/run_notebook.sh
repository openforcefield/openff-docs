#!/bin/bash

set -Ee -o pipefail
shopt -s failglob

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    MICROMAMBA=./micromamba-linux-64
elif [[ "$OSTYPE" == "darwin"* ]]; then
    MICROMAMBA=./micromamba-osx-64
else
    echo "OS type $OSTYPE is not supported by $0"
    echo "For detailed install instructions, see"
    echo "https://docs.openforcefield.org/en/latest/install.html"
    exit 1
fi

PREFIX='./env'

unset PYTHONPATH
unset PYTHONHOME

$MICROMAMBA create --file environment.yaml --prefix "$PREFIX"
eval "$($MICROMAMBA shell hook --shell=bash)"
micromamba activate "$PREFIX"
jupyter notebook *.ipynb
