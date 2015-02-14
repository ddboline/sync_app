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
from collections import defaultdict, namedtuple

class FileInfo(object):
    ''' file info class '''
    __slots__ = ['filename', 'urlname', 'md5sum', 'filestat']

    stat_attrs = ('st_atime', 'st_blksize', 'st_blocks', 'st_ctime', 'st_dev', 'st_gid', 'st_ino', 'st_mode', 'st_mtime', 'st_nlink', 'st_rdev', 'st_size', 'st_uid')
    
    stat_tuple = namedtuple('empty_stat_result', stat_attrs)
    
    empty_stat = stat_tuple(**{attr: 0 for attr in stat_attrs})
    
    def __init__(self, fn='', url='', md5='', fs=None):
        self.filename = fn
        self.urlname = url
        if md5:
            self.md5sum = md5
        else:
            self.md5sum = self.get_md5()
        self.filestat = None
        if fs:
            if all(hasattr(fs, attr) for attr in stat_attrs):
                self.filestat = fs
        if not self.filestat:
            self.filestat = self.get_stat()

    def __repr__(self):
        return '<FileInfo(fn=%s, url=%s, md5=%s, size=%s>' % (self.filename, self.urlname, self.md5sum, self.filestat.st_size)
    
    def get_md5(self):
        return None
    
    def get_stat(self):
        return None

class FileList(object):
    ''' file list class '''
    def __init__(self, filelist=None):
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
        fn = os.path.basename(file_info_obj.filename)
        md = file_info_obj.md5sum
        self.filelist.append(file_info_obj)
        self.filelist_name_dict[fn].append(file_info_obj)
        self.filelist_md5_dict[md].append(file_info_obj)
    
    def fill_dicts(self):
        for f in self.filelist:
            self.append(f)
