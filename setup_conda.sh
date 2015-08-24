#!/bin/bash

sudo /opt/conda/bin/conda install -c https://conda.anaconda.org/ddboline --yes boto dateutil pip pytz nose google-api-python-client

scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/ddboline_personal_scripts/client_secrets.json sync_app/
scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/ddboline_personal_scripts/*.dat .
