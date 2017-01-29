#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Compare two directories
    first run to identify new files, modified files
    second run to copy new files, most recently modified files
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os

from sync_app.util import MIMETYPE_SUFFIXES, GOOGLEAPP_MIMETYPES


def compare_objects(obj0, obj1, use_sha1=False):
    """ should obj0 replace obj1? """
    if obj0.filename != obj1.filename:
        # different filenames
        return False
    md50 = obj0.md5sum
    md51 = obj1.md5sum
    sha0 = obj0.sha1sum
    sha1 = obj1.sha1sum
    fmtim0 = obj0.filestat.st_mtime
    fmtim1 = obj1.filestat.st_mtime
    if ('application/vnd.google-apps' in getattr(obj0, 'mimetype', '')
            and os.path.exists(obj0.filename)):
        if fmtim0 > fmtim1:
            return True
    if use_sha1:
        if sha0 and sha1 and sha0 == sha1:
            # identical files
            return False
    else:
        if md50 and md51 and md50 == md51:
            # identical files
            return False
    if fmtim0 > fmtim1:
        # obj0 is newer than obj1
        return True


class FileSync(object):
    """ Sync Directories """
    def __init__(self, flists=None):
        """ Init function """
        self.flists = []
        if flists:
            for flist in flists:
                if not all(hasattr(flist, x) for x in ('filelist',
                           'filelist_md5_dict', 'filelist_name_dict')):
                    continue
                self.flists.append(flist)

    def __repr__(self):
        return '%s' % ' '.join(self.flists)

    def compare_lists(self, callback0=None, callback1=None, use_sha1=False):
        """ Compare file lists """
        if len(self.flists) < 2:
            return None

        list_a_not_b = []
        list_b_not_a = []

        for fn_ in self.flists[0].filelist_name_dict:
            finfo0 = self.flists[0].filelist_name_dict[fn_]
            _md = finfo0[0].md5sum
            fmd5_0 = _md if _md else finfo0[0].get_md5()
            if use_sha1:
                _sh = finfo0[0].sha1sum
                fmd5_0 = _sh if _sh else finfo0[0].get_sha1()
            fmtim0 = finfo0[0].filestat.st_mtime
            for flist in self.flists[1:]:
                hash_dict = flist.filelist_md5_dict
                if use_sha1:
                    hash_dict = flist.filelist_sha1_dict
                if fn_ not in flist.filelist_name_dict:
                    fn_exists = False
                    fmtim1 = -1
                    for finf in finfo0:
                        if ('application/vnd.google-apps'
                                in getattr(finf, 'mimetype', '')):
                            mtype = getattr(finf, 'mimetype')
                            mtype = GOOGLEAPP_MIMETYPES.get(mtype)
                            ext = MIMETYPE_SUFFIXES.get(mtype)
                            fnexp = '%s.%s' % (finf.filename, ext)
                            if (os.path.exists(finf.filename)
                                    or os.path.exists(fnexp)):
                                fn_exists = True
                                fmtim1 = finf.filestat.st_mtime
                    if fn_exists:
                        continue
                    list_a_not_b.append(finfo0)
                elif fmd5_0 not in hash_dict:
                    tmp = flist.filelist_name_dict[fn_][0]
                    fmd5_1 = tmp.md5sum if tmp.md5sum else tmp.get_md5()
                    if use_sha1:
                        fmd5_1 = tmp.sha1sum if tmp.sha1sum else tmp.get_sha1()
                    fmtim1 = tmp.filestat.st_mtime
                    fmtim1 += 12 * 3600
                    if fmtim0 > fmtim1:
                        print('compare lists', fn_, fmd5_0, fmd5_1, fmtim0,
                              fmtim1)
                    if fmd5_0 != fmd5_1 and fmtim0 > fmtim1:
                        print('compare fn=%s, ' % fn_ +
                              'fname=%s, ' % tmp.filename +
                              'ft0=%s, ft1=%s, ' % (fmtim0, fmtim1) +
                              'fm0=%s, fm1=%s' % (fmd5_0, fmd5_1))
                        list_a_not_b.append(finfo0)

        for flist in self.flists[1:]:
            for fn_, finfo1 in flist.filelist_name_dict.items():
                if fn_ not in self.flists[0].filelist_name_dict:
                    tmp = fn_.split('.')[-2:]
                    if len(tmp) > 1 and tmp[0] == tmp[1]:
                        test = '.'.join(fn_.split('.')[:-1])
                        if test in self.flists[0].filelist_name_dict:
                            continue
                    fn_exists = False
                    for finf in finfo1:
                        if finf.filename in self.flists[0].filelist:
                            fn_exists = True
                    if fn_exists:
                        continue
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


def test_file_sync():
    """ test FileSync """
    tmp = FileSync(flists=range(20))
    assert '%s' % tmp == ''
