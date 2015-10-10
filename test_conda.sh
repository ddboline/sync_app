#!/bin/bash

nosetests --with-coverage --cover-package=sync_app tests/*.py sync_app/*.py
