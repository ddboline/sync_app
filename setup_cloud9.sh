#!/bin/bash

sudo cp -a ${HOME}/.ssh /root/
sudo chown -R root:root /root/
sudo bash -c "echo deb ssh://ddboline@ddbolineathome.mooo.com/var/www/html/deb/xenial/devel ./ > /etc/apt/sources.list.d/py2deb2.list"
sudo apt-get update
sudo apt-get install -y --force-yes python-boto python-googleapi \
                                    python-dateutil python-pytest \
                                    python-pytest-cov python-onedrivesdk \
                                    python-setuptools python-dev python-futures

scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/sync_app/sync_app/client_secrets.json sync_app/
scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/sync_app/*.dat .
scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/sync_app/session.pkl .
mkdir ~/.onedrive
scp ddboline@ddbolineathome.mooo.com:~/.onedrive/credentials ~/.onedrive/
