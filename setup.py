#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 18:29:26 2015

@author: ddboline
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
import sys
from setuptools import setup

console_scripts = (('sync-app',
                    'sync_app.sync_utils:sync_arg_parse'), ('list-drive-files',
                                                            'sync_app.sync_utils:list_drive_parse'),
                   ('list-onedrive-files', 'sync_app.sync_utils:list_onedrive_parse'),
                   ('list-box-files',
                    'sync_app.sync_utils:list_box_parse'), ('list-s3-files',
                                                            'sync_app.sync_utils:parse_s3_args'))

if sys.version_info.major == 2:
    console_scripts = ['%s = %s' % (x, y) for x, y in console_scripts]
else:
    v = sys.version_info.major
    console_scripts = ['%s%s = %s' % (x, v, y) for x, y in console_scripts]

setup(
    name='sync_app',
    version='0.0.4.8',
    author='Daniel Boline',
    author_email='ddboline@gmail.com',
    description='sync_app',
    long_description='Sync App',
    license='MIT',
    install_requires=['boto', 'google-api-python-client'],
    packages=['sync_app'],
    package_dir={'sync_app': 'sync_app'},
    entry_points={
        'console_scripts': console_scripts
    })
