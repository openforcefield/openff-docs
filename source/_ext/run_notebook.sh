#!/bin/bash

set -Ee -o pipefail
shopt -s failglob

# Make sure we're in the same directory as this script,
# the environment file, and the notebook
cd "${0%/*}"

ARCH="64"
OS=$(uname)

if [[ "$OS" == "Linux" ]]; then
    PLATFORM="linux"
elif [[ "$OS" == "Darwin" ]]; then
    PLATFORM="osx";
else
    echo "OS $OS is not supported by $0"
    echo "For detailed install instructions, see"
    echo "https://docs.openforcefield.org/en/latest/install.html"
    exit 1
fi

if [[ ! -f ./micromamba ]]; then
    echo "Downloading micromamba"
    curl -L# https://micro.mamba.pm/api/micromamba/$PLATFORM-$ARCH/latest | tar -xvj --strip-components=1 bin/micromamba
fi

PREFIX='./env'

unset PYTHONPATH
unset PYTHONHOME

if [[ -d $PREFIX/conda-meta/ ]]; then
    ./micromamba update --file environment.yaml --prefix "$PREFIX"
else
    ./micromamba create --file environment.yaml --prefix "$PREFIX"
fi

eval "$(./micromamba shell hook --shell=bash)"
micromamba activate "$PREFIX"
jupyter notebook *.ipynb
