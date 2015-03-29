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
        if not flist0 or not flist1:
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

        list_a_not_b = []
        list_b_not_a = []

        for fn in self.flists[0].filelist_name_dict:
            index = 1
            for flist in self.flists[1:]:
                if fn not in flist.filelist_name_dict:
                    list_a_not_b.append((self.flists[0].filelist_name_dict[fn], index))
                index += 1

        index = 0
        for flist in self.flists[1:]:
            for fn in flist.filelist_name_dict:
                if fn not in self.flists[0]:
                    list_b_not_a.append((index, flist.filelist_name_dict[fn]))
            index += 1

        print list_a_not_b
        print list_b_not_a
