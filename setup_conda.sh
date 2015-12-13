#!/bin/bash

sudo /opt/conda/bin/conda install -c https://conda.anaconda.org/ddboline --yes \
        boto dateutil pip pytz nose google-api-python-client coverage

### TODO: how do I fix this in conda build?
sudo chmod a+r /opt/conda/lib/python3.*/site-packages/httplib2/cacerts.txt

scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/sync_app/sync_app/client_secrets.json sync_app/
scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/sync_app/*.dat .
scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/sync_app/session.pkl .
mkdir ~/.onedrive
scp ddboline@ddbolineathome.mooo.com:~/.onedrive/credentials ~/.onedrive/
