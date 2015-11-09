#!/bin/bash

sudo cp -a ${HOME}/.ssh /root/
sudo chown -R root:root /root/
sudo bash -c "echo deb ssh://ddboline@ddbolineathome.mooo.com/var/www/html/deb/trusty/devel ./ > /etc/apt/sources.list.d/py2deb2.list"
sudo apt-get update
sudo apt-get install -y python-boto python-googleapi python-dateutil python-nose python-coverage python-onedrivesdk

scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/sync_app/sync_app/client_secrets.json sync_app/
scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/sync_app/*.dat .
scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/sync_app/session.pkl .
