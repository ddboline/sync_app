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
    """ GDrive File Info """
    __slots__ = FileInfo.__slots__ + ['gdriveid', 'mimetype', 'parentid',
                                      'exporturls', 'exportpath', 'isroot']

    def __init__(self, gid='', fn='', md5=''):
        """ Init Function """
        FileInfo.__init__(self, fn=fn, md5=md5)
        self.gdriveid = gid
        self.mimetype = ''
        self.parentid = ''
        self.exportpath = ''
        self.isroot = False
        self.exporturls = {}

    def download(self, gdrive):
        expfile = '%s/%s' % (self.exportpath, self.filename)
        return gdrive.download(self.urlname, expfile)

    def __repr__(self):
        """ nice string representation """
        return '<FileInfoGdrive(fn=%s, ' % self.filename +\
               'url=%s, ' % self.urlname +\
               'path=%s, '% self.exportpath +\
               'md5=%s, ' % self.md5sum +\
               'size=%s, ' % self.filestat.st_size +\
               'st_mime=%s, ' % self.filestat.st_mtime +\
               'id=%s, ' % self.gdriveid +\
               'pid=%s, ' % self.parentid +\
               'isroot=%s>' % self.isroot


class FileListGdrive(FileList):
    """ GDrive File List """

    def __init__(self, filelist=None, basedir=None, gdrive=None):
        """ Init Function """
        FileList.__init__(self, filelist=filelist, basedir=basedir,
                          filelist_type='gdrive')
        self.filelist_id_dict = {}
        self.directory_id_dict = {}
        self.directory_name_dict = {}
        self.gdrive = gdrive

    def append(self, finfo):
        """ overload FileList.append """
        FileList.append(self, finfo)
        self.filelist_id_dict[finfo.gdriveid] = finfo

    def append_item(self, item):
        """ append file to FileList, fill dict's """
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
            finfo.isroot = item['parents'][0]['isRoot']
        finfo.exportpath = self.get_export_path(finfo, abspath=False)
        finfo.urlname = 'gdrive://%s/%s' % (finfo.exportpath, finfo.filename)
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
        """ append directory to FileList """
        finfo = FileInfoGdrive()
        if item['mimeType'] != 'application/vnd.google-apps.folder':
            return finfo
        finfo.gdriveid = item['id']
        finfo.filename = item['title']
        finfo.mimetype = item['mimeType']
        if len(item['parents']) > 0:
            finfo.parentid = item['parents'][0]['id']
            finfo.isroot = item['parents'][0]['isRoot']
        self.append(finfo)
        self.filelist_id_dict[finfo.gdriveid] = finfo
        self.directory_id_dict[finfo.gdriveid] = finfo
        self.directory_name_dict[finfo.filename] = finfo

    def get_export_path(self, finfo, abspath=True):
        """ determine export path for given finfo object"""
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
        fullpath = '/'.join(fullpath[::-1])
        fullpath = fullpath.replace('My Drive', BASE_DIR)
        if abspath:
            fullpath = os.path.dirname(fullpath)
        return fullpath

    def fix_export_path(self):
        """ determine export paths for finfo objects in file list"""
        for finfo in self.filelist:
            finfo.exportpath = self.get_export_path(finfo)

    def fill_file_list_gdrive(self, number_to_process=-1):
        """ fill GDrive file list"""
        if not self.gdrive:
            self.gdrive = GdriveInstance()
        self.gdrive.number_to_process = number_to_process
        self.gdrive.get_folders(self.append_dir)
        self.gdrive.list_files(self.append_item)
        print('update paths')
        self.fix_export_path()

    def create_directory(self, dname):
        pid_ = None
        dn_list = dname.replace(BASE_DIR + '/', '').split('/')

        if dn_list[0] in self.directory_name_dict \
                and self.directory_name_dict[dn_list[0]].isroot:
            pid_ = self.directory_name_dict[dn_list[0]].gdriveid
        else:
            pid_ = self.gdrive.create_directory(dn_list[0], parent_id=pid_)
        for dn_ in dn_list[1:]:
            if dn_ in self.directory_name_dict \
                    and pid_ == self.directory_name_dict[dn_].parentid:
                pid_ = self.directory_name_dict[dn_].gdriveid
            else:
                pid_ = self.gdrive.create_directory(dn_, parent_id=pid_)
        return pid_

    def delete_directory(self, dname):
        pid_list = []
        dn_list = dname.replace(BASE_DIR + '/', '').split('/')

        if dn_list[0] in self.directory_name_dict \
                and self.directory_name_dict[dn_list[0]].isroot:
            pid_ = self.directory_name_dict[dn_list[0]].gdriveid
            pid_list.append(pid_)
        else:
            return ''
        for dn_ in dn_list[1:]:
            if dn_ in self.directory_name_dict \
                    and pid_ == self.directory_name_dict[dn_].parentid:
                pid_ = self.directory_name_dict[dn_].gdriveid
                pid_list.append(pid_)
            else:
                return ''
        for pid in pid_list[::-1]:
            self.gdrive.delete_file(pid)
        return ''

    def upload_file(self, fname, pathname=None):
        """ upload file """
        dname = os.path.dirname(fname)
        if pathname:
            dname = pathname
        pid_ = self.create_directory(dname)
        return self.gdrive.upload(fname, parent_id=pid_)
