#!/bin/bash

sudo /opt/conda/bin/conda install -c https://conda.anaconda.org/ddboline --yes \
        boto dateutil pip pytz nose google-api-python-client coverage

### TODO: how do I fix this in conda build?
sudo chmod a+r /opt/conda/lib/python3.4/site-packages/httplib2/cacerts.txt

scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/ddboline_personal_scripts/client_secrets.json sync_app/
scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/ddboline_personal_scripts/*.dat .
