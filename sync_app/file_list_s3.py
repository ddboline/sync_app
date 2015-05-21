#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    extract FileInfo object for files in AWS S3
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from sync_app.file_list import FileInfo, FileList
from sync_app.s3_instance import S3Instance

class FileInfoS3(FileInfo):
    """ File Info for S3, add bucket metadata """
    __slots__ = FileInfo.__slots__ + ['bucket']

    def __init__(self, fn='', md5='', fs=None, bk=''):
        FileInfo.__init__(self, fn=fn, md5=md5, fs=fs)
        self.bucket = bk


class FileListS3(FileList):
    """ File list for S3 """

    def __init__(self, filelist=None, bucket=None, s3=None):
        """ Init function """
        FileList.__init__(self, filelist=filelist, basedir=bucket,
                          filelist_type='s3')
        self.bucketlist = []
        self.s3 = s3
        pass

    def append_item(self, item):
        """ append S3 item to filelist """
        finfo = FileInfoS3()
        finfo.filename = item.key
        finfo.bucket = item.bucket.name
        finfo.urlname = 's3://%s/%s' % (finfo.bucket, finfo.filename)
        finfo.md5sum = item.etag.replace('"','')
        if finfo.filename in self.filelist_name_dict:
            for ffn in self.filelist_name_dict[finfo.filename]:
                if ffn.md5sum == finfo.md5sum:
                    return self.filelist_name_dict[finfo.filename]
        self.append(finfo)
        return finfo

    def fill_file_list_s3(self, bucket=None):
        """ fill s3 filelist  """
        self.s3 = S3Instance()
        self.s3.get_list_of_keys(callback_fn=self.append_item)
