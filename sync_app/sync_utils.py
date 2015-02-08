#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    Utility functions
'''

def get_md5(fname):
    if not os.path.exists(fname):
        return None
    m = hashlib.md5()
    with open(fname, 'r') as infile:
        for line in infile:
            m.update(line)
    return m.hexdigest()
