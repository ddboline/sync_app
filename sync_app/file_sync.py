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

        list_a_not_b = []
        list_b_not_a = []

        for fn in self.flists[0].filelist_name_dict:
            finfo0 = self.flists[0].filelist_name_dict[fn]
            fmd5_0 = finfo0[0].md5sum
            fmtim0 = finfo0[0].filestat.st_mtime
            for flist in self.flists[1:]:
                if fn not in flist.filelist_name_dict:
                    list_a_not_b.append(finfo0)
                elif fmd5_0 not in flist.filelist_md5_dict:
                    fmd5_1 = flist.filelist_name_dict[fn][0].get_md5()
                    fmtim1 = flist.filelist_name_dict[fn][0].get_stat().st_mtime
                    fmtim1 += 12 * 3600
                    if fmd5_0 != fmd5_1 and fmtim0 > fmtim1:
                        print(fn, fmtim0, fmtim1, fmd5_0, fmd5_1)
                        list_a_not_b.append(finfo0)

        for flist in self.flists[1:]:
            for fn, finfo1 in flist.filelist_name_dict.items():
                if fn not in self.flists[0].filelist_name_dict:
                    list_b_not_a.append(finfo1)

        for finfo in list_a_not_b:
            if callback0:
                finf_ = finfo
                if type(finf_) == list:
                    finf_ = finfo[0]
                callback0(finf_)

        for finfo in list_b_not_a:
            if callback1:
                finf_ = finfo
                if type(finf_) == list:
                    finf_ = finfo[0]
                callback1(finf_)
