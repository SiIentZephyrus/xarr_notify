#!/bin/sh

set -e
apt update
apt install -y cron libsasl2-dev python-dev libldap2-dev libssl-dev
pip install --upgrade pip
pip install -r ../requirements.txt
chmod -R 777 ./run.sh
