#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    module containing FileInfo class.
    FileInfo:
        container for file metadata:
            filename
            urlname
            md5sum of the file
            sha1sum of the file
            output of os.stat
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)

STAT_ATTRS = ('st_mtime', 'st_size')
FILE_INFO_SLOTS = ('filename', 'urlname', 'md5sum', 'sha1sum', 'filestat')


class StatTuple(object):
    """
        StatTuple class
        intended as generalization of object returned by os.stat
        scaled back to just contain modification time and size...
    """
    __slots__ = STAT_ATTRS

    def __init__(self, fs=None, **kwargs):
        """ Init function """
        self.st_mtime = 0
        self.st_size = 0
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
        return '<StatTuple(size=%s)>' % self.st_size


class FileInfo(object):
    """
        file info class, meant as a base for local/gdrive/s3,
        define common elements, hold common code
    """
    __slots__ = list(FILE_INFO_SLOTS)

    def __init__(self, fn='', url='', md5=None, sha1=None, fs=None, in_tuple=None):
        """ Init function, define sensible defaults """
        self.filename = fn
        self.urlname = url
        self.md5sum = md5 if md5 else self.get_md5()
        self.sha1sum = sha1 if sha1 else self.get_sha1()
        self.filestat = StatTuple(fs) if fs else StatTuple(self.get_stat())
        if in_tuple:
            self.input_cache_tuple(in_tuple)

    def __repr__(self):
        """ Nice pretty string representation """
        return '<FileInfo(fn=%s, ' % self.filename + \
               'url=%s, ' % self.urlname + \
               'md5=%s, ' % self.md5sum + \
               'sha1=%s, ' % self.sha1sum + \
               'size=%s)>' % self.filestat.st_size

    def fill_stat(self, fs=None, **options):
        """ convert fs into StatTuple... """
        self.filestat = StatTuple(fs=fs, **options)

    def get_md5(self):
        """ meant to be overridden """
        self.md5sum = ''
        return self.md5sum

    def get_sha1(self):
        self.sha1sum = ''
        return self.sha1sum

    def get_stat(self):
        """ meant to be overridden """
        self.filestat = StatTuple()
        return self.filestat

    def output_cache_tuple(self):
        """ serialize FileInfo """
        if hasattr(self.md5sum, 'result'):
            self.md5sum = self.md5sum.result()
        if hasattr(self.sha1sum, 'result'):
            self.sha1sum = self.sha1sum.result()
        return (self.filename, self.urlname, self.md5sum, self.sha1sum, self.filestat.st_mtime,
                self.filestat.st_size)

    def input_cache_tuple(self, in_tuple):
        """ deserialize FileInfo """
        self.filename, self.urlname, self.md5sum, self.sha1sum, \
            self.filestat.st_mtime, self.filestat.st_size = in_tuple


def test_stat_tuple():
    """ test StatTuple class """
    test_dict = {'st_mtime': 1234567, 'st_size': 7654321}
    tmp = StatTuple(**test_dict)
    obs = '%s' % tmp
    exp = '<StatTuple(size=7654321)>'
    assert obs == exp
    assert tmp.st_size == 7654321


def test_file_info():
    """ test FileInfo class """
    import os
    test_dict = {'st_mtime': 1234567, 'st_size': 7654321}
    fs_ = StatTuple(**test_dict)
    fn_ = 'tests/test_dir/hello_world.txt'
    tmp = FileInfo(
        fn=fn_,
        url='file://%s' % os.path.abspath(fn_),
        md5='8ddd8be4b179a529afa5f2ffae4b9858',
        sha1='a0b65939670bc2c010f4d5d6a0b3e4e4590fb92b',
        fs=fs_)
    test = {
        'filename': 'tests/test_dir/hello_world.txt',
        'md5sum': '8ddd8be4b179a529afa5f2ffae4b9858',
        'sha1sum': 'a0b65939670bc2c010f4d5d6a0b3e4e4590fb92b'
    }

    for key in FILE_INFO_SLOTS:
        if key == 'urlname':
            continue
        if key == 'filestat':
            assert tmp.filestat.st_size == 7654321
        else:
            print(key, getattr(tmp, key))
            print(key, test[key])
            assert getattr(tmp, key) == test[key]
