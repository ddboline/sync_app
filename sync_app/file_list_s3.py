#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    extract FileInfo object for files in AWS S3
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from sync_app.file_list import FileInfo, FileList

from dateutil.parser import parse

BASE_DIR = '%s/S3' % os.getenv('HOME')

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
        self.filename = item.key
        self.bucket = item.bucket.name
        self.urlname = 's3://%s/%s' % (self.bucket, self.filename)
        self.md5sum = item.etag.replace('"','')
        _temp = {'st_size': item.size,
                 'st_mtime': int(parse(item.last_modified).strftime("%s"))}
        self.fill_stat(**_temp)

    def output_cache_tuple(self):
        return (self.filename, self.urlname, self.md5sum,
                self.filestat.st_mtime, self.filestat.st_size, self.bucket)

    def input_cache_tuple(self, in_tuple):
        self.filename, self.urlname, self.md5sum, self.filestat.st_mtime,\
        self.filestat.st_size, self.bucket = in_tuple


class FileListS3(FileList):
    """ File list for S3 """

    def __init__(self, filelist=None, bucket=None, s3=None):
        """ Init function """
        FileList.__init__(self, filelist=filelist, basedir=bucket,
                          filelist_type='s3')
        self.s3 = s3
        self.filelist_key_dict = {}

    def __getitem__(self, key):
        if key in self.filelist_key_dict:
            return self.filelist_key_dict[key]
        else:
            return self.FileList.__getitem__(self, key)

    def append_item(self, item):
        """ append S3 item to filelist """
        finfo = FileInfoS3(item=item)
        if finfo.filename in self:
            for ffn in self.filelist_name_dict[finfo.filename]:
                if ffn.md5sum == finfo.md5sum:
                    return self.filelist_name_dict[finfo.filename]
        self.append(finfo)
        self.filelist_key_dict[finfo.filename] = finfo
        return finfo

    def fill_file_list_s3(self, bucket=None):
        """ fill s3 filelist  """
        self.s3.get_list_of_keys(callback_fn=self.append_item)
