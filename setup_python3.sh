#!/bin/bash

### hack...
export LANG="C.UTF-8"

sudo bash -c "echo deb ssh://ddboline@ddbolineathome.mooo.com/var/www/html/deb/trusty/python3/devel ./ > /etc/apt/sources.list.d/py2deb2.list"
sudo apt-get update
sudo apt-get install -y --force-yes python3-boto python3-google-api-python-client \
                                    python3-dateutil python3-nose python3-setuptools \
                                    python3-requests python3-coverage python3-onedrivesdk

scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/sync_app/sync_app/client_secrets.json sync_app/
scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/sync_app/*.dat .
scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/sync_app/session.pkl .
mkdir ~/.onedrive
scp ddboline@ddbolineathome.mooo.com:~/.onedrive/credentials ~/.onedrive/
