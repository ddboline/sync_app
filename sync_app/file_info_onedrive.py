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

FILE_INFO_SLOTS = ('onedriveid', 'mimetype', 'exportpath',
                   'onedrive', 'sha1sum', 'parentid')


class FileInfoOneDrive(FileInfo):
    """ OneDrive File Info """
    __slots__ = FileInfo.__slots__ + list(FILE_INFO_SLOTS)

    def __init__(self, gid='', fn='', md5='', onedrive=None, item=None,
                 in_tuple=None, mime='', sha1sum=None):
        FileInfo.__init__(self, fn=fn, md5=md5)
        self.onedriveid = gid
        self.onedrive = onedrive
        self.mimetype = mime
        self.exportpath = ''
        self.sha1sum = ''
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
            return self.onedrive.download(self.onedriveid, self.filename,
                                          sha1sum=self.sha1sum)
        else:
            path_ = '%s/%s' % (BASE_DIR, self.filename)
            return self.onedrive.download(self.urlname, path_,
                                          sha1sum=self.sha1sum)

    def __repr__(self):
        """ nice string representation """
        return '<FileInfoOneDrive(fn=%s, ' % self.filename +\
               'url=%s, ' % self.urlname +\
               'path=%s, ' % self.exportpath +\
               'md5=%s, ' % self.md5sum +\
               'sha1sum=%s, ' % self.sha1sum +\
               'size=%s, ' % self.filestat.st_size +\
               'st_mime=%s, ' % self.filestat.st_mtime +\
               'id=%s)>' % self.onedriveid

    def output_cache_tuple(self):
        return (self.filename, self.urlname, self.md5sum, self.sha1sum,
                self.filestat.st_mtime, self.filestat.st_size, self.onedriveid,
                self.mimetype, self.exportpath, self.onedrive)

    def input_cache_tuple(self, in_tuple):
        self.filename, self.urlname, self.md5sum, self.sha1sum, \
            self.filestat.st_mtime, self.filestat.st_size, self.onedriveid, \
            self.mimetype, self.exportpath, self.onedrive = in_tuple

    def fill_item(self, item):
        """ fill FileInfoOneDrive from item """
        self.onedriveid = item['id']
        self.filename = item['name']
        self.parentid = item['parentid']
        if 'file' in item:
            self.mimetype = item['file'].get('mimeType', 'None')
            if 'hashes' in item['file']:
                self.sha1sum = item['file']['hashes'].get('sha1Hash',
                                                          '').lower()


def test_file_info_onedrive():
    """ Test FileInfoOneDrive """
    assert True
