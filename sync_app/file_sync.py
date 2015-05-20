#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Compare two directories
    first run to identify new files, modified files
    second run to copy new files, most recently modified files
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class FileSync(object):
    """ Sync Directories """
    def __init__(self, flists=None):
        """ Init function """
        if not flists:
            return None
        self.flists = []
        for flist in flists:
            if not hasattr(flist, 'filelist') or\
               not hasattr(flist, 'filelist_md5_dict') or\
               not hasattr(flist, 'filelist_name_dict'):
                continue
            self.flists.append(flist)

    def compare_lists(self, callback0=None, callback1=None):
        """ Compare file lists """
        if len(self.flists) < 2:
            return None

        for flist in self.flists:
            print(len(flist.filelist_name_dict))

        list_a_not_b = []
        list_b_not_a = []

        for fn in self.flists[0].filelist_name_dict:
            for flist in self.flists[1:]:
                if fn not in flist.filelist_name_dict:
                    list_a_not_b.append(self.flists[0].filelist_name_dict[fn])

        for flist in self.flists[1:]:
            for fn in flist.filelist_name_dict:
                if fn not in self.flists[0].filelist_name_dict:
                    list_b_not_a.append(flist.filelist_name_dict[fn])

        for finf_ in list_a_not_b:
            if callback0:
                callback0(finf_[0])

        for finf_ in list_b_not_a:
            if callback1:
                callback1(finf_[0])
