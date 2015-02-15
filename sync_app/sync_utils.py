#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    Utility functions
'''
import os
import hashlib

from sync_app.util import run_command

def get_md5_old(fname):
    if not os.path.exists(fname):
        return None
    m = hashlib.md5()
    with open(fname, 'r') as infile:
        for line in infile:
            m.update(line)
    return m.hexdigest()

def get_md5(fname):
    if not os.path.exists(fname):
        return None
    output = run_command('md5sum %s' % fname, do_popen=True).read().split()[0]
    return output
