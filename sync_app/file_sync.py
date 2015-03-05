#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    Compare two directories
    first run to identify new files, modified files
    second run to copy new files, most recently modified files
'''

from collections import defaultdict

class FileSync(object):
    def __init__(self, flists=None):
        if not flists:
            return None
        self.flists = []
        for flist in flists:
            if not hasattr(flist, 'filelist') or\
               not hasattr(flist, 'filelist_md5_dict') or\
               not hasattr(flist, 'filelist_name_dict'):
                   continue
            self.flists.append(flist)

    def compare_lists(self):
        if len(self.flists) < 2:
            return None
        
        fname_count = defaultdict(list)
        
        for n, flist in enumerate(self.flists):
            for fn in flist.filelist_name_dict:
                fname_count[fn].append(n)
        
        for fn in fname_count:
            if len(fname_count[fn]) != len(self.flists):
                print fn, fname_count[fn]
