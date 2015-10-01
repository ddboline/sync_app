#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 18:29:26 2015

@author: ddboline
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

from setuptools import setup

setup(
    name='sync_app',
    version='0.0.2',
    author='Daniel Boline',
    author_email='ddboline@gmail.com',
    description='sync_app',
    long_description='Sync App',
    license='MIT',
    install_requires=['boto', 'google-api-python-client'],
    packages=['sync_app'],
    package_dir={'sync_app': 'sync_app'},
    package_data={'sync_app': ['templates/*.html']},
    entry_points={'console_scripts': 
                  ['sync-app = sync_app.sync_utils:sync_arg_parse',
                   'list_drive_files = sync_app.sync_utils:list_drive_parse',
                   'list_s3_files = sync_app.sync_utils:parse_s3_args']}
)
