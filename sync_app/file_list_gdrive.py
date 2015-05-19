#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    extract FileInfo object for files in gdrive
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from dateutil.parser import parse

from sync_app.file_list import FileInfo, FileList
from sync_app.gdrive_instance import GdriveInstance

BASE_DIR = '/home/ddboline/gDrive'

class FileInfoGdrive(FileInfo):
    __slots__ = FileInfo.__slots__ + ['gdriveid', 'mimetype', 'parentid',
                                      'exporturls', 'exportpath']

    def __init__(self, gid='', fn='', md5=''):
        FileInfo.__init__(self, fn=fn, md5=md5)
        self.gdriveid = gid
        self.mimetype = ''
        self.parentid = ''
        self.exportpath = ''
        self.exporturls = {}

    def __repr__(self):
        return '<FileInfoGdrive(fn=%s, url=%s, path=%s, md5=%s, size=%s,' \
               % (self.filename, self.urlname, self.exportpath, self.md5sum,
                  self.filestat.st_size) \
               + 'st_mtime=%s, id=%s, mime=%s, pid=%s>' \
                   % (self.filestat.st_mtime, self.gdriveid, self.mimetype,
                      self.parentid)


class FileListGdrive(FileList):
    def __init__(self, filelist=None, basedir=None):
        FileList.__init__(self, filelist=filelist, basedir=basedir,
                          filelist_type='gdrive')
        self.filelist_id_dict = {}
        self.directory_id_dict = {}
        self.directory_name_dict = {}
        self.gdrive = None

    def append(self, finfo):
        FileList.append(self, finfo)
        self.filelist_id_dict[finfo.gdriveid] = finfo

    def append_item(self, item):
        finfo = FileInfoGdrive()
        finfo.gdriveid = item['id']
        finfo.filename = item['title']
        if 'md5Checksum' in item:
            finfo.md5sum = item['md5Checksum']
        _temp = {}
        if all(it in item for it in ['createdDate', 'modifiedDate',
                                     'fileSize']):
            _temp = {'st_mtime': parse(item['modifiedDate']).strftime("%s"),
                     'st_size': item['fileSize']}
        finfo.fill_stat(**_temp)
        finfo.mimetype = item['mimeType']
        if len(item['parents']) > 0:
            finfo.parentid = item['parents'][0]['id']
        else:
            finfo.parentid = ''
        finfo.urlname = 'gdrive://%s/%s' % (finfo.parentid, finfo.filename)
        if 'downloadUrl' in item:
            finfo.urlname = item['downloadUrl']
        if 'exportLinks' in item:
            finfo.exporturls = item['exportLinks']
            elmime = None
            prefered_formats = ['vnd.oasis.opendocument', 'text/', 'image/png',
                                'image/jpeg', 'application/pdf']
            for pfor in prefered_formats:
                for mime in finfo.exporturls:
                    if not elmime and pfor in mime:
                        elmime = mime
            if elmime:
                finfo.urlname = finfo.exporturls[elmime]

        if finfo.gdriveid in self.filelist_id_dict:
            return finfo
        if finfo.filename in self.filelist_name_dict:
            for ffn in self.filelist_name_dict[finfo.filename]:
                if finfo.md5sum == ffn.md5sum:
                    return finfo
        self.append(finfo)
        self.filelist_id_dict[finfo.gdriveid] = finfo
        return finfo

    def append_dir(self, item):
        finfo = FileInfoGdrive()
        if item['mimeType'] != 'application/vnd.google-apps.folder':
            return finfo
        finfo.gdriveid = item['id']
        finfo.filename = item['title']
        finfo.mimetype = item['mimeType']
        if len(item['parents']) > 0:
            finfo.parentid = item['parents'][0]['id']
        else:
            finfo.parentid = ''
        self.append(finfo)
        self.filelist_id_dict[finfo.gdriveid] = finfo
        self.directory_id_dict[finfo.gdriveid] = finfo
        self.directory_name_dict[finfo.filename] = finfo

    def get_export_path(self, finfo):
        fullpath = [finfo.filename]
        pid = finfo.parentid
        while pid:
            if pid in self.filelist_id_dict:
                finf = self.filelist_id_dict[pid]
                pid = finf.parentid
                fullpath.append(finf.filename)
            else:
                if not self.gdrive:
                    self.gdrive = GdriveInstance()
                request = self.gdrive.service.files().get(fileId=pid)
                response = request.execute()
                finf = self.append_item(response)
                pid = finf.parentid
                fullpath.append(finf.filename)
        return '/'.join(fullpath[::-1])

    def fix_export_path(self):
        for finfo in self.filelist:
            finfo.exportpath = os.path.dirname(self.get_export_path(finfo))
            finfo.exportpath = finfo.exportpath.replace('My Drive', BASE_DIR)

    def fill_file_list_gdrive(self, number_to_process=-1):
        self.gdrive = GdriveInstance(number_to_process=number_to_process)
        self.gdrive.list_files(self.append_item)
        self.gdrive.get_folders(self.append_dir)
        print('update paths')
        self.fix_export_path()
