#!/bin/sh

set -e
pip install --upgrade pip
pip install -r ./requirements.txt
mv config/config.example.yml config/config.yml
chmod -R 777 build/run.sh
