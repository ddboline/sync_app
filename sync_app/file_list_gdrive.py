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

GDRIVE_MIMETYPES = (
'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
'text/csv', 'image/png', 'application/vnd.oasis.opendocument.text',
'application/pdf')

FILE_INFO_SLOTS = ('gdriveid', 'mimetype', 'parentid', 'exporturls',
                   'exportpath', 'isroot', 'gdrive')

class FileInfoGdrive(FileInfo):
    """ GDrive File Info """
    __slots__ = FileInfo.__slots__ + list(FILE_INFO_SLOTS)

    def __init__(self, gid='', fn='', md5='', gdrive=None, item=None):
        """ Init Function """
        for attr in FILE_INFO_SLOTS:
            setattr(self, attr, '')
        FileInfo.__init__(self, fn=fn, md5=md5)
        self.gdriveid = gid
        self.isroot = False
        self.exporturls = {}
        self.gdrive = gdrive
        if item:
            self.fill_item(item)

    def download(self):
        if BASE_DIR in self.filename:
            return self.gdrive.download(self.urlname, self.filename,
                                        md5sum=self.md5sum)
        else:
            path_ = '%s/%s' % (BASE_DIR, self.filename)
            return self.gdrive.download(self.urlname, path_,
                                        md5sum=self.md5sum)

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

    def fill_item(self, item):
        fext = ''
        self.gdriveid = item['id']
        self.filename = item['title']
        if 'md5Checksum' in item:
            self.md5sum = item['md5Checksum']
        _temp = {}
        if 'modifiedDate' in item:
            _temp['st_mtime'] = int(parse(item['modifiedDate']).strftime("%s"))
        if 'fileSize' in item:
            _temp['st_size'] = item['fileSize']
        self.fill_stat(**_temp)
        self.mimetype = item['mimeType']
        if len(item['parents']) > 0:
            self.parentid = item['parents'][0]['id']
            self.isroot = item['parents'][0]['isRoot']
        if self.mimetype == 'application/vnd.google-apps.folder':
            return
        if 'downloadUrl' in item:
            self.urlname = item['downloadUrl']
        elif 'exportLinks' in item:
            self.exporturls = item['exportLinks']
            elmime = None
            for pfor in GDRIVE_MIMETYPES:
                for mime in self.exporturls:
                    if not elmime and pfor in mime:
                        elmime = mime
            if elmime:
                self.urlname = self.exporturls[elmime]
                fext = self.urlname.split('exportFormat=')[1]
        if 'fileExtension' in item:
            fext = item['fileExtension']
        if fext not in self.filename.lower():
            self.filename += '.%s' % fext


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

    def __getitem__(self, key):
        for dict_ in (self.filelist_id_dict, self.directory_id_dict,
                      self.directory_name_dict):
            if key in dict_:
                return dict_[key]
        return self.FileList.__getitem__(self, key)

    def append(self, finfo):
        """ overload FileList.append """
        FileList.append(self, finfo)
        self.filelist_id_dict[finfo.gdriveid] = finfo

    def append_item(self, item):
        """ append file to FileList, fill dict's """
        finfo = FileInfoGdrive(gdrive=self.gdrive, item=item)

        ### Fix paths
        finfo.exportpath = self.get_export_path(finfo, abspath=False)
        if not finfo.urlname:
            finfo.urlname = 'gdrive://%s' % (finfo.exportpath)
        finfo.filename = '%s/%s' % (finfo.exportpath,
                                    os.path.basename(finfo.filename))

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
        finfo = FileInfoGdrive(gdrive=self.gdrive, item=item)
        if item['mimeType'] != 'application/vnd.google-apps.folder':
            return finfo

        self.filelist_id_dict[finfo.gdriveid] = finfo
        self.directory_id_dict[finfo.gdriveid] = finfo
        self.directory_name_dict[finfo.filename] = finfo

    def get_export_path(self, finfo, abspath=True, is_dir=False):
        """ determine export path for given finfo object"""
        fullpath = []
        if is_dir:
            fullpath.append(finfo.filename)
        pid = finfo.parentid
        while pid:
            if pid in self.filelist_id_dict:
                finf = self.filelist_id_dict[pid]
                pid = finf.parentid
                fullpath.append(os.path.basename(finf.filename))
            else:
                if not self.gdrive:
                    self.gdrive = GdriveInstance()
                request = self.gdrive.service.files().get(fileId=pid)
                response = request.execute()
                finf = self.append_item(response)
                pid = finf.parentid
                fullpath.append(os.path.basename(finf.filename))
        fullpath = '/'.join(fullpath[::-1])
        fullpath = fullpath.replace('My Drive', BASE_DIR)
        if abspath:
            fullpath = os.path.dirname(fullpath)
        return fullpath

    def fix_export_path(self):
        """ determine export paths for finfo objects in file list"""
        for finfo in self.filelist:
            finfo.exportpath = self.get_export_path(finfo)
        for id_, finfo in self.directory_id_dict.items():
            finfo.exportpath = self.get_export_path(finfo, is_dir=True)

    def fill_file_list_gdrive(self, number_to_process=-1):
        """ fill GDrive file list"""
        if not self.gdrive:
            self.gdrive = GdriveInstance()
        self.gdrive.number_to_process = number_to_process
        print('get_folders')
        self.gdrive.get_folders(self.append_dir)
        print('list_files')
        self.gdrive.list_files(self.append_item)
        print('update paths')

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
