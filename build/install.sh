#!/bin/sh

set -e
pip install --upgrade pip
pip install -r ./requirements.txt
chmod -R 777 build/run.sh
