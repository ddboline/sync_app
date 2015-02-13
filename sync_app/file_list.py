#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    module containing FileInfo and FileList classes.
    FileInfo:
        container for file metadata:
            filename
            urlname
            md5sum of the file
            output of os.stat
    FileList:
        container for list of FileInfo object
        dicts to efficiently search within filelist
'''
import os
from collections import defaultdict

class FileInfo(object):
    ''' file info class '''
    __slots__ = ['filename', 'urlname', 'md5sum', 'filestat']

    stat_attrs = ('st_atime', 'st_blksize', 'st_blocks', 'st_ctime', 'st_dev', 'st_gid', 'st_ino', 'st_mode', 'st_mtime', 'st_nlink', 'st_rdev', 'st_size', 'st_uid')

    def __init__(self, fn='', pn='', hn='localhost', url='', md5='', fs=None):
        self.filename = fn
        self.urlname = url
        self.md5sum = md5
        self.filestat = fs
        if urlname[:7] == 'file://' and os.path.exists('%s' % self.filename):
            _md5 = get_md5_full('%s' % self.filename)
            self.md5sum = _md5
            _fstat = os.stat(self.filename)
            self.filestat = {attr: getattr(_fstat, attr) for attr in self.stat_attrs}

    def __repr__(self):
        return '<FileInfo(fn=%s, hs=%s, md5=%s, size=%s>' % (self.fullfilename,
      

class FileList(object):
    ''' file list class '''
    def __init__(self, basepath='', subdirectories=None, filelist=None):
        if basepath:
            self.basepath = basepath
        else:
            self.basepath = '.'
        if subdirectories:
            self.subdirs = ['%s/%s' % (self.basepath, subdirectories)]
        else:
            self.subdirs = [self.basepath]
        self.filelist = []
        self.filelist_name_dict = defaultdict(list)
        self.filelist_md5_dict = defaultdict(list)

        if filelist:
            self.filelist = filelist
            self.fill_dicts()
    
    def append(self, file_info_obj):
        for at in ['filename', 'urlname', 'md5sum', 'filestat']:
            if not hasattr(file_info_obj, at):
                return False
        fn = os.path.basename(self.file_info_obj)
        md = self.file_info_obj.md5sum
        self.filelist.append(file_info_obj)
        self.filelist_name_dict[fn].append(file_info_obj)
        self.filelist_md5_dict[md].append(file_info_obj)
    
    def fill_dicts(self):
        for f in self.filelist:
            self.append(f)
