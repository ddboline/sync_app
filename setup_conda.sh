#!/bin/bash

sudo /opt/conda/bin/conda install --yes boto dateutil pip pytz 

sudo /opt/conda/bin/pip install --upgrade google-api-python-client

scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/ddboline_personal_scripts/client_secrets.json sync_app/
scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/ddboline_personal_scripts/*.dat .
