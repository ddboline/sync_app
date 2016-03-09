#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    extract FileInfo object for files in box
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import datetime
from dateutil.parser import parse

from sync_app.file_info import FileInfo

BASE_DIR = '%s/Box' % os.getenv('HOME')

FILE_INFO_SLOTS = ('boxid', 'mimetype', 'exportpath',
                   'box', 'sha1sum', 'parentid')


class FileInfoBox(FileInfo):
    """ Box File Info """
    __slots__ = FileInfo.__slots__ + list(FILE_INFO_SLOTS)

    def __init__(self, gid='', fn='', sha1='', box=None, item=None,
                 in_tuple=None, mime='', sha1sum=None, pid='0'):
        FileInfo.__init__(self, fn=fn, sha1=sha1)
        self.boxid = gid
        self.box = box
        self.mimetype = mime
        self.exportpath = ''
        self.sha1sum = sha1
        self.parentid = pid
        if item:
            self.fill_item(item)
        if in_tuple:
            self.input_cache_tuple(in_tuple)

    def delete(self):
        """ wrapper around BoxInstance.delete_file """
        return self.box.delete_file(self.boxid)

    def download(self):
        """ wrapper around BoxInstance.download """
        if BASE_DIR in self.filename:
            return self.box.download(self.boxid, self.filename,
                                     sha1sum=self.sha1sum)
        else:
            path_ = '%s/%s' % (BASE_DIR, self.filename)
            return self.box.download(self.boxid, path_, sha1sum=self.sha1sum)

    def __repr__(self):
        """ nice string representation """
        return '<FileInfoBox(fn=%s, ' % self.filename +\
               'url=%s, ' % self.urlname +\
               'path=%s, ' % self.exportpath +\
               'sha1sum=%s, ' % self.sha1sum +\
               'size=%s, ' % self.filestat.st_size +\
               'st_mime=%s, ' % self.filestat.st_mtime +\
               'pid=%s, ' % self.parentid +\
               'id=%s)>' % self.boxid

    def output_cache_tuple(self):
        return (self.filename, self.urlname, self.sha1sum,
                self.filestat.st_mtime, self.filestat.st_size, self.boxid,
                self.mimetype, self.exportpath, self.box)

    def input_cache_tuple(self, in_tuple):
        self.filename, self.urlname, self.sha1sum, \
            self.filestat.st_mtime, self.filestat.st_size, self.boxid, \
            self.mimetype, self.exportpath, self.box = in_tuple

    def fill_item(self, item):
        """ fill FileInfoBox from item """
        self.boxid = item['id']
        self.filename = item['name']
        self.parentid = item['parentid']

        _temp = {}
        if 'modified_at' in item:
            _temp['st_mtime'] = int(parse(item['modified_at']).strftime("%s"))
        else:
            _temp['st_mtime'] = int(datetime.datetime.now().strftime("%s"))
        _temp['st_size'] = item.get('size', 0)
        self.fill_stat(**_temp)
        self.sha1sum = item.get('sha1', '')


def test_file_info_box():
    """ Test FileInfoBox """
    tmp = FileInfoBox(gid='0BxGM0lfCdptnNzJsblNEa1ZzUU0',
                      sha1='63f959b57ab0d1ef4e96a8dc4df3055456a80705',
                      fn='/home/ddboline/Box/temp1.xml')
    test = '<FileInfoBox(fn=/home/ddboline/Box/temp1.xml, ' \
           'url=, path=, sha1sum=63f959b57ab0d1ef4e96a8dc4df3055456a80705, ' \
           'size=0, st_mime=0, pid=0, id=0BxGM0lfCdptnNzJsblNEa1ZzUU0)>'
    print(tmp)
    assert '%s' % tmp == test

    test_tuple = tmp.output_cache_tuple()
    tmp = FileInfoBox(in_tuple=test_tuple)

    assert '%s' % tmp == test
    return
