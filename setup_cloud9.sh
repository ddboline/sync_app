#!/bin/bash

sudo apt-get update
sudo apt-get install -y python-boto python-googleapi

scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/aws_scripts/keys_20150119.tar.gz .
scp ddboline@ddbolineathome.mooo.com:~/setup_files/build/ddboline_personal_scripts/*.dat .
