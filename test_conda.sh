#!/bin/bash

python3 ./tests/sync_app_unittests_local.py
python3 ./tests/sync_app_unittests_s3.py
python3 ./tests/sync_app_unittests_gdrive.py
