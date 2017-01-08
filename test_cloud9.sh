#!/bin/bash

pytest --cov=sync_app sync_app/*.py tests/*.py

# pyreverse sync_app
# for N in classes packages; do dot -Tps ${N}*.dot > ${N}.ps ; done
