#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    extract FileInfo object for files in AWS S3
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from dateutil.parser import parse

from .file_info import FileInfo


class FileInfoS3(FileInfo):
    """ File Info for S3, add bucket metadata """
    __slots__ = FileInfo.__slots__ + ['bucket']

    def __init__(self, fn='', md5='', fs=None, bk='', item=None,
                 in_tuple=None):
        FileInfo.__init__(self, fn=fn, md5=md5, fs=fs)
        self.bucket = bk
        if item:
            self.fill_item(item)
        if in_tuple:
            self.input_cache_tuple(in_tuple)

    def fill_item(self, item):
        """ Fill FileInfoS3 from item """
        self.filename = item.key
        self.bucket = item.bucket.name
        self.urlname = 's3://%s/%s' % (self.bucket, self.filename)
        self.md5sum = item.etag.replace('"', '')
        _temp = {'st_size': item.size,
                 'st_mtime': int(parse(item.last_modified).strftime("%s"))}
        self.fill_stat(**_temp)

    def output_cache_tuple(self):
        return (self.filename, self.urlname, self.md5sum,
                self.filestat.st_mtime, self.filestat.st_size, self.bucket)

    def input_cache_tuple(self, in_tuple):
        self.filename, self.urlname, self.md5sum, self.filestat.st_mtime,\
        self.filestat.st_size, self.bucket = in_tuple
