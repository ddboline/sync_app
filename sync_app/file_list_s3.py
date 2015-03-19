#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    extract FileInfo object for files in AWS S3
'''

import os

from sync_app.file_list import FileInfo, FileList
from sync_app.s3_instance import S3Instance

class FileInfoS3(FileInfo):
    __slots__ = FileInfo.__slots__ + ['bucket']
    
    def __init__(self, fn='', md5='', fs=None, bk=''):
        FileInfo.__init__(self, fn=fn, md5=md5, fs=fs)
        self.bucket = bk
        

class FileListS3(FileList):
    def __init__(self, filelist=None, bucket=None):
        FileList.__init__(self, filelist=filelist, basedir=bucket, filelist_type='s3')
        self.bucketlist = []
        self.s3 = None
        pass

    def append_item(self, item):
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
        self.s3 = S3Instance()
        self.s3.get_list_of_keys(callback_fn=self.append_item)
