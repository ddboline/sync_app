#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    extract FileInfo object for files in onedrive
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
from dateutil.parser import parse

from sync_app.file_info import FileInfo

BASE_DIR = '%s/OneDrive' % os.getenv('HOME')

FILE_INFO_SLOTS = ('onedriveid', 'mimetype', 'exportpath',
                   'onedrive', 'sha1sum', 'parentid')


class FileInfoOneDrive(FileInfo):
    """ OneDrive File Info """
    __slots__ = FileInfo.__slots__ + list(FILE_INFO_SLOTS)

    def __init__(self, gid='', fn='', sha1='', onedrive=None, item=None,
                 in_tuple=None, mime='', sha1sum=None, pid='root'):
        FileInfo.__init__(self, fn=fn, sha1=sha1)
        self.onedriveid = gid
        self.onedrive = onedrive
        self.mimetype = mime
        self.exportpath = ''
        self.sha1sum = sha1
        self.parentid = pid
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
               'sha1sum=%s, ' % self.sha1sum +\
               'size=%s, ' % self.filestat.st_size +\
               'st_mime=%s, ' % self.filestat.st_mtime +\
               'pid=%s, ' % self.parentid +\
               'id=%s)>' % self.onedriveid

    def output_cache_tuple(self):
        return (self.filename, self.urlname, self.sha1sum,
                self.filestat.st_mtime, self.filestat.st_size, self.onedriveid,
                self.mimetype, self.exportpath, self.onedrive)

    def input_cache_tuple(self, in_tuple):
        self.filename, self.urlname, self.sha1sum, \
            self.filestat.st_mtime, self.filestat.st_size, self.onedriveid, \
            self.mimetype, self.exportpath, self.onedrive = in_tuple

    def fill_item(self, item):
        """ fill FileInfoOneDrive from item """
        self.onedriveid = item['id']
        self.filename = item['name']
        self.parentid = item['parentid']
        _temp = {}
        _temp['st_mtime'] = int(
            parse(item['lastModifiedDateTime']).strftime("%s"))
        _temp['st_size'] = item['size']
        self.fill_stat(**_temp)
        if 'file' in item:
            self.mimetype = item['file'].get('mimeType', 'None')
            if 'hashes' in item['file']:
                self.sha1sum = item['file']['hashes'].get('sha1Hash',
                                                          '').lower()


def test_file_info_onedrive():
    """ Test FileInfoOneDrive """
    tmp = FileInfoOneDrive(gid='0BxGM0lfCdptnNzJsblNEa1ZzUU0',
                           sha1='63f959b57ab0d1ef4e96a8dc4df3055456a80705',
                           fn='/home/ddboline/OneDrive/temp1.xml')
    test = '<FileInfoOneDrive(fn=/home/ddboline/OneDrive/temp1.xml, ' \
           'url=, path=, sha1sum=63f959b57ab0d1ef4e96a8dc4df3055456a80705, ' \
           'size=0, st_mime=0, pid=root, id=0BxGM0lfCdptnNzJsblNEa1ZzUU0)>'
    print(tmp)
    assert '%s' % tmp == test

    test_tuple = tmp.output_cache_tuple()
    tmp = FileInfoOneDrive(in_tuple=test_tuple)

    assert '%s' % tmp == test
