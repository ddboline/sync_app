#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 18:29:26 2015

@author: ddboline
"""
from __future__ import print_function
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

from distutils.core import setup

setup(
    name='sync_app',
    version='00.00.01',
    author='Daniel Boline',
    author_email='ddboline@gmail.com',
    description='sync_app',
    long_description='Sync App',
    license='MIT',
#    install_requires=['pandas >= 0.13.0', 'numpy >= 1.8.0'],
    packages=['sync_app'],
    package_dir={'sync_app': 'sync_app'},
    package_data={'sync_app': ['templates/*.html']},
    scripts=['sync.py', 'list_drive_files.py', 'list_s3_files.py']
)
