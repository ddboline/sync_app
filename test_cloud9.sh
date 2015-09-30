#!/bin/bash

nosetests --with-coverage --cover-package=sync_app tests/*.py sync_app/*.py

# pyreverse sync_app
# for N in classes packages; do dot -Tps ${N}*.dot > ${N}.ps ; done
