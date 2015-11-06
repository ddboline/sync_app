#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    extract FileInfo object for files in onedrive
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from .file_info import FileInfo

BASE_DIR = '%s/OneDrive' % os.getenv('HOME')

FILE_INFO_SLOTS = ('gdriveid', 'mimetype', 'parentid', 'exporturls',
                   'exportpath', 'isroot', 'onedrive')


class FileInfoOneDrive(FileInfo):
    """ OneDrive File Info """
    __slots__ = FileInfo.__slots__ + list(FILE_INFO_SLOTS)

    def __init__(self, gid='', fn='', md5='', onedrive=None, item=None,
                 in_tuple=None, mime='', pid=None):
        FileInfo.__init__(self, fn=fn, md5=md5)
        self.onedriveid = gid
        self.isroot = False
        self.exporturls = {}
        self.onedrive = onedrive
        self.mimetype = mime
        self.parentid = pid
        self.exportpath = ''
        if item:
            self.fill_item(item)
        if in_tuple:
            self.input_cache_tuple(in_tuple)

    def delete(self):
        """ wrapper around OneDriveInstance.delete_file """
        return self.onedrive.delete_file(self.onedriveid)

    def download(self):
        """ wrapper around OneDriveInstance.download """
        if BASE_DIR in self.filename:
            return self.onedrive.download(self.urlname, self.filename,
                                          md5sum=self.md5sum)
        else:
            path_ = '%s/%s' % (BASE_DIR, self.filename)
            return self.onedrive.download(self.urlname, path_,
                                          md5sum=self.md5sum)

    def __repr__(self):
        """ nice string representation """
        return '<FileInfoOneDrive(fn=%s, ' % self.filename +\
               'url=%s, ' % self.urlname +\
               'path=%s, ' % self.exportpath +\
               'md5=%s, ' % self.md5sum +\
               'size=%s, ' % self.filestat.st_size +\
               'st_mime=%s, ' % self.filestat.st_mtime +\
               'id=%s, ' % self.onedriveid +\
               'pid=%s, ' % self.parentid +\
               'isroot=%s)>' % self.isroot

    def output_cache_tuple(self):
        return (self.filename, self.urlname, self.md5sum,
                self.filestat.st_mtime, self.filestat.st_size, self.onedriveid,
                self.mimetype, self.parentid, self.exporturls, self.exportpath,
                self.isroot, self.onedrive)

    def input_cache_tuple(self, in_tuple):
        self.filename, self.urlname, self.md5sum, self.filestat.st_mtime, \
            self.filestat.st_size, self.onedriveid, self.mimetype, \
            self.parentid, self.exporturls, self.exportpath, self.isroot, \
            self.onedrive = in_tuple

    def fill_item(self, item):
        """ fill FileInfoOneDrive from item """
        raise NotImplementedError


def test_file_info_onedrive():
    """ Test FileInfoOneDrive """
    assert True
