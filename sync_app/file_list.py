#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
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
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from collections import defaultdict

STAT_ATTRS = ('st_mtime', 'st_size')
FILE_LIST_TYPES = ('local', 'remote', 'gdrive', 's3')
FILE_INFO_SLOTS = ('filename', 'urlname', 'md5sum', 'filestat')

class StatTuple(object):
    """
        StatTuple class
        intended as generalization of object returned by os.stat
        scaled back to just contain modification time and size...
    """
    __slots__ = STAT_ATTRS

    def __init__(self, fs=None, **kwargs):
        """ Init function """
        for attr in STAT_ATTRS:
            if attr in kwargs:
                val = kwargs[attr]
                setattr(self, attr, int(val))
            else:
                setattr(self, attr, 0)
        if fs:
            for attr in STAT_ATTRS:
                if hasattr(fs, attr):
                    val = getattr(fs, attr)
                    setattr(self, attr, int(val))

    def __repr__(self):
        """ Nice pretty string representation """
        return '<StatTuple(size=%s, mtime=%s)>' % (self.st_size, self.st_mtime)

class FileInfo(object):
    """
        file info class, meant as a base for local/gdrive/s3,
        define common elements, hold common code
    """
    __slots__ = list(FILE_INFO_SLOTS)

    def __init__(self, fn='', url='', md5=None, fs=None, in_tuple=None):
        """ Init function, define sensible defaults """
        self.filename = fn
        self.urlname = url
        self.md5sum = md5 if md5 else self.get_md5()
        self.filestat = StatTuple(fs) if fs else StatTuple(self.get_stat())
        if in_tuple:
            self.input_cache_tuple(in_tuple)

    def __repr__(self):
        """ Nice pretty string representation """
        return '<FileInfo(fn=%s, ' % self.filename +\
               'url=%s, ' % self.urlname +\
               'md5=%s, ' % self.md5sum +\
               'size=%s, ' % self.filestat.st_size +\
               'st_mtime=%s)>' % self.filestat.st_mtime

    def fill_stat(self, fs=None, **options):
        """ convert fs into StatTuple... """
        self.filestat = StatTuple(fs=fs, **options)

    def get_md5(self):
        """ meant to be overridden """
        return ''

    def get_stat(self):
        """ meant to be overridden """
        return StatTuple()

    def output_cache_tuple(self):
        return (self.filename, self.urlname, self.md5sum,
                self.filestat.st_mtime, self.filestat.st_size)

    def input_cache_tuple(self, in_tuple):
        self.filename, self.urlname, self.md5sum, self.filestat.st_mtime,\
        self.filestat.st_size = in_tuple

class FileList(object):
    """ file list class """
    def __init__(self, filelist=None, filelist_type=None, basedir=None):
        self.filelist = filelist if filelist else {}
        self.filelist_name_dict = defaultdict(list)
        self.filelist_md5_dict = defaultdict(list)
        self.filelist_type = filelist_type if filelist_type else 'local'
        self.basedir = basedir if basedir else os.getenv('HOME')
        self.baseurl = 'local://'
        self.fill_dicts()

    @property
    def filelist(self):
        return self.__filelist

    @filelist.setter
    def filelist(self, val):
        """ make a copy of list, element by element """
        self.__filelist = {}
        for k, v in val.items():
            if k not in self.__filelist:
                self.__filelist[k] = v

    @property
    def filelist_type(self):
        return self.__filelist_type

    @filelist_type.setter
    def filelist_type(self, val):
        """ throw error if we get unexpected value """
        if val in FILE_LIST_TYPES:
            self.__filelist_type = val
        else:
            raise ValueError

    def __getitem__(self, key):
        """ try to simplify calling a bit... """
        if key in self.filelist_md5_dict:
            return self.filelist_md5_dict.__getitem__(key)
        elif key in self.filelist_name_dict:
            return self.filelist_name_dict.__getitem__(key)
        else:
            return self.filelist.__getitem__(key)

    def __iter__(self):
        return iter(self.filelist.values())

    def append(self, file_info_obj):
        for at in ['filename', 'urlname', 'md5sum', 'filestat']:
            if not hasattr(file_info_obj, at):
                raise ValueError('this object won\'t work')
        ffn_ = file_info_obj.filename
        if ffn_ in self.filelist:
            self.filelist[ffn_] = file_info_obj
            return
        fn_ = os.path.basename(ffn_)
        md5 = file_info_obj.md5sum
        self.filelist[ffn_] = file_info_obj
        self.filelist_name_dict[fn_].append(file_info_obj)
        self.filelist_md5_dict[md5].append(file_info_obj)

    def fill_dicts(self):
        for f in self.filelist:
            self.append(f)
