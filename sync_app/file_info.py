#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    module containing FileInfo class.
    FileInfo:
        container for file metadata:
            filename
            urlname
            md5sum of the file
            output of os.stat
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

STAT_ATTRS = ('st_mtime', 'st_size')
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

def test_stat_tuple():
    test_dict = {'st_mtime': 1234567, 'st_size': 7654321}
    tmp = '%s' % StatTuple(**test_dict)
    test = '<StatTuple(size=7654321, mtime=1234567)>'
    assert tmp == test

def test_file_info():
    import os
    test_dict = {'st_mtime': 1234567, 'st_size': 7654321}
    fs_ = StatTuple(**test_dict)
    fn_ = 'tests/test_dir/hello_world.txt'
    tmp = '%s' % FileInfo(fn=fn_, url='file://%s' % os.path.abspath(fn_),
                          md5='8ddd8be4b179a529afa5f2ffae4b9858', fs=fs_)
    test = '<FileInfo(fn=tests/test_dir/hello_world.txt, ' + \
           'url=file:///home/ddboline/setup_files/build/sync_app/' + \
           'tests/test_dir/hello_world.txt, ' + \
           'md5=8ddd8be4b179a529afa5f2ffae4b9858, size=7654321, ' + \
           'st_mtime=1234567)>'
    assert tmp == test
