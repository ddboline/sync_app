#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    extract FileInfo object for files in gdrive
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

from sync_app.file_info import FileInfo

from dateutil.parser import parse

BASE_DIR = '%s/gDrive' % os.getenv('HOME')

GOOGLEAPP_MIMETYPES = {
    'application/vnd.google-apps.document':
    'application/vnd.oasis.opendocument.text',
    'application/vnd.google-apps.drawing': 'image/png',
    'application/vnd.google-apps.form': 'application/pdf',
    'application/vnd.google-apps.map': 'application/pdf',
    'application/vnd.google-apps.presentation': 'application/pdf',
    'application/vnd.google-apps.spreadsheet':
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}

GDRIVE_MIMETYPES = (
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/csv', 'image/png', 'application/vnd.oasis.opendocument.text',
    'application/pdf')

FILE_INFO_SLOTS = ('gdriveid', 'mimetype', 'parentid', 'exporturls',
                   'exportpath', 'isroot', 'gdrive')


class FileInfoGdrive(FileInfo):
    """ GDrive File Info """
    __slots__ = FileInfo.__slots__ + list(FILE_INFO_SLOTS)

    def __init__(self, gid='', fn='', md5='', gdrive=None, item=None,
                 in_tuple=None, mime='', pid=None):
        FileInfo.__init__(self, fn=fn, md5=md5)
        self.gdriveid = gid
        self.isroot = False
        self.exporturls = {}
        self.gdrive = gdrive
        self.mimetype = mime
        self.parentid = pid
        self.exportpath = ''
        if item:
            self.fill_item(item)
        if in_tuple:
            self.input_cache_tuple(in_tuple)

    def delete(self):
        """ wrapper around GDriveInstance.delete_file """
        return self.gdrive.delete_file(self.gdriveid)

    def download(self):
        """ wrapper around GDriveInstance.download """
        export_mimetype = GOOGLEAPP_MIMETYPES.get(self.mimetype, None)
        if BASE_DIR in self.filename:
            return self.gdrive.download(self.gdriveid, self.filename,
                                        md5sum=self.md5sum,
                                        export_mimetype=export_mimetype)
        else:
            path_ = '%s/%s' % (BASE_DIR, self.filename)
            return self.gdrive.download(self.gdriveid, path_,
                                        md5sum=self.md5sum,
                                        export_mimetype=export_mimetype)

    def __repr__(self):
        """ nice string representation """
        return '<FileInfoGdrive(fn=%s, ' % self.filename +\
               'url=%s, ' % self.urlname +\
               'path=%s, ' % self.exportpath +\
               'md5=%s, ' % self.md5sum +\
               'size=%s, ' % self.filestat.st_size +\
               'st_mime=%s, ' % self.filestat.st_mtime +\
               'mime=%s, ' % self.mimetype +\
               'id=%s, ' % self.gdriveid +\
               'pid=%s, ' % self.parentid +\
               'isroot=%s)>' % self.isroot

    def output_cache_tuple(self):
        return (self.filename, self.urlname, self.md5sum,
                self.filestat.st_mtime, self.filestat.st_size, self.gdriveid,
                self.mimetype, self.parentid, self.exporturls, self.exportpath,
                self.isroot, self.gdrive)

    def input_cache_tuple(self, in_tuple):
        self.filename, self.urlname, self.md5sum, self.filestat.st_mtime, \
            self.filestat.st_size, self.gdriveid, self.mimetype, \
            self.parentid, self.exporturls, self.exportpath, self.isroot, \
            self.gdrive = in_tuple

    def fill_item(self, item):
        """ fill FileInfoGdrive from item """
        fext = ''
        self.gdriveid = item['id']
        self.filename = item['name']
        if 'md5Checksum' in item:
            self.md5sum = item['md5Checksum']
        _temp = {}
        if 'modifiedDate' in item:
            _temp['st_mtime'] = int(parse(item['modifiedDate']).strftime("%s"))
        if 'fileSize' in item:
            _temp['st_size'] = item['fileSize']
        self.fill_stat(**_temp)
        self.mimetype = item['mimeType']
        item_parents = item.get('parents', [])
        if len(item_parents) > 0:
            self.parentid = item['parents'][0]
        if self.mimetype == 'application/vnd.google-apps.folder':
            return
        if 'webContentLink' in item:
            self.urlname = item['webContentLink']
        if 'fileExtension' in item:
            fext = item['fileExtension']
        if fext not in self.filename.lower():
            self.filename += '.%s' % fext


def test_file_info_gdrive():
    """ Test FileInfoGdrive """
    tmp = FileInfoGdrive(gid='0BxGM0lfCdptnNzJsblNEa1ZzUU0',
                         md5='b9c44ab2be80575b6dde114e17156189',
                         mime='application/x-tar',
                         fn='/home/ddboline/gDrive/image_backup/' +
                            'chromebook_home_backup_Linux_ip-172-31-14-57' +
                            '_3_13_0-61-generic_x86_64_x86_64_x86_64_GNU_' +
                            'Linux_20150818.tar.gz')
    test = '<FileInfoGdrive(fn=/home/ddboline/gDrive/image_backup/' + \
           'chromebook_home_backup_Linux_ip-172-31-14-57_3_13_0-61' + \
           '-generic_x86_64_x86_64_x86_64_GNU_Linux_20150818.tar.gz, ' + \
           'url=, path=, md5=b9c44ab2be80575b6dde114e17156189, size=0, ' + \
           'st_mime=0, mime=application/x-tar, ' + \
           'id=0BxGM0lfCdptnNzJsblNEa1ZzUU0, pid=None, ' + \
           'isroot=False)>'
    print(tmp)
    assert '%s' % tmp == test

    test_tuple = tmp.output_cache_tuple()
    tmp = FileInfoGdrive(in_tuple=test_tuple)

    print(tmp)
    assert '%s' % tmp == test
