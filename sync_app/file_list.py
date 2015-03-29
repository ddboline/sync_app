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

STAT_ATTRS = ('st_mtime', 'st_size')
FILE_LIST_TYPES = ('local', 'remote', 'gdrive', 's3')

class StatTuple(object):
    __slots__ = STAT_ATTRS

    def __init__(self, **kwargs):
        for attr in STAT_ATTRS:
            if attr in kwargs:
                setattr(self, attr, kwargs[attr])
            else:
                setattr(self, attr, None)

class FileInfo(object):
    ''' file info class '''
    __slots__ = ['filename', 'urlname', 'md5sum', 'filestat']

    def __init__(self, fn='', url='', md5='', fs=None):
        self.filename = fn
        self.urlname = url
        if md5:
            self.md5sum = md5
        else:
            self.md5sum = self.get_md5()
        self.filestat = StatTuple()
        if not fs:
            fs = self.get_stat()
        if fs:
            self.fill_stat(fs)

    def __repr__(self):
        return '<FileInfo(fn=%s, url=%s, md5=%s, size=%s, st_mtime=%s>'\
                % (self.filename, self.urlname, self.md5sum,
                   self.filestat.st_size, self.filestat.st_mtime)

    def fill_stat(self, fs=None, **options):
        _temp = {attr: 0 for attr in STAT_ATTRS}
        if fs:
            for attr in STAT_ATTRS:
                if hasattr(fs, attr):
                    _temp[attr] = getattr(fs, attr)
        else:
            for attr in STAT_ATTRS:
                if attr in options:
                    _temp[attr] = options[attr]
        self.filestat = StatTuple(**_temp)


    def get_md5(self):
        return None

    def get_stat(self):
        return None

class FileList(object):
    ''' file list class '''
    def __init__(self, filelist=None, filelist_type=None, basedir=None):
        self.filelist = []
        self.filelist_name_dict = defaultdict(list)
        self.filelist_md5_dict = defaultdict(list)
        self.filelist_type = 'local'
        self.baseurl = 'local://'
        self.basedir = '/home/ddboline'

        if filelist_type in FILE_LIST_TYPES:
            self.filelist_type = filelist_type

        if basedir:
            self.basedir = basedir

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
