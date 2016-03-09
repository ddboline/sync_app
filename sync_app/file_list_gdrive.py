#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    extract FileList object for files in gdrive
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
from collections import defaultdict

from sync_app.file_list import FileList
from sync_app.gdrive_instance import GdriveInstance
from sync_app.file_info_gdrive import BASE_DIR, FileInfoGdrive


class FileListGdrive(FileList):
    """ GDrive File List """

    def __init__(self, filelist=None, basedir=None, gdrive=None):
        """ Init Function """
        FileList.__init__(self, filelist=filelist, basedir=basedir,
                          filelist_type='gdrive')
        self.filelist_id_dict = {}
        self.directory_id_dict = {}
        self.directory_name_dict = defaultdict(dict)
        self.gdrive = gdrive
        self.root_directory = None

    def __getitem__(self, key):
        for dict_ in (self.filelist_id_dict, self.directory_id_dict,
                      self.directory_name_dict):
            if key in dict_:
                return dict_[key]
        return FileList.__getitem__(self, key)

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

        if finfo.isroot:
            self.root_directory = finfo
        self.filelist_id_dict[finfo.gdriveid] = finfo
        self.directory_id_dict[finfo.gdriveid] = finfo
        self.directory_name_dict[finfo.filename][finfo.parentid] = finfo

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
        if not fullpath:
            fullpath = 'My Drive'
        elif 'My Drive' not in fullpath:
            fullpath = 'My Drive/' + fullpath
        elif 'New Folder' in fullpath:
            raise Exception('Do not want New Folder')
        fullpath = fullpath.replace('My Drive', BASE_DIR)
        if abspath:
            fullpath = os.path.dirname(fullpath)
        return fullpath

    def fix_export_path(self):
        """ determine export paths for finfo objects in file list"""
        for finfo in self.filelist.values():
            finfo.exportpath = self.get_export_path(finfo)
        for _, finfo in self.directory_id_dict.items():
            finfo.exportpath = self.get_export_path(finfo, is_dir=True)

    def fill_file_list(self, number_to_process=-1, searchstr=None,
                       verbose=True):
        """ fill GDrive file list"""
        if not self.gdrive:
            self.gdrive = GdriveInstance()
        if verbose:
            print('get_folders')
        self.gdrive.number_to_process = -1
        self.gdrive.get_folders(self.append_dir)
        if verbose:
            print('list_files')
        self.gdrive.number_to_process = number_to_process
        self.gdrive.items_processed = 0
        self.gdrive.list_files(self.append_item, searchstr=searchstr)
        self.fill_hash_dicts()
        if verbose:
            print('update paths')

    def get_or_create_directory(self, dname):
        """ create directory on gdrive """
        pid_ = None
        if self.root_directory:
            pid_ = self.root_directory.parentid
        dn_list = dname.replace(BASE_DIR, '').split('/')
        if dn_list and dn_list[0] == '':
            dn_list.pop(0)
        if not dn_list:
            return pid_

        if dn_list[0] in self.directory_name_dict \
                and pid_ in self.directory_name_dict[dn_list[0]] \
                and self.directory_name_dict[dn_list[0]][pid_].isroot:
            pid_ = self.directory_name_dict[dn_list[0]][pid_].gdriveid
        else:
            pid_ = self.gdrive.create_directory(dn_list[0], parent_id=pid_)
        for dn_ in dn_list[1:]:
            if dn_ in self.directory_name_dict \
                    and pid_ in self.directory_name_dict[dn_]:
                pid_ = self.directory_name_dict[dn_][pid_].gdriveid
            else:
                pid_ = self.gdrive.create_directory(dn_, parent_id=pid_)
        return pid_

    def delete_directory(self, dname):
        """ delete directory on gdrive """
        pid_list = []
        dn_list = dname.replace(BASE_DIR + '/', '').split('/')

        if dn_list[0] in self.directory_name_dict:
            if list(self.directory_name_dict[dn_list[0]].values())[0].isroot:
                pid_ = list(
                    self.directory_name_dict[dn_list[0]].values())[0].gdriveid
                pid_list.append(pid_)
            else:
                return ''
        else:
            return ''
        for dn_ in dn_list[1:]:
            if dn_ in self.directory_name_dict \
                    and pid_ in self.directory_name_dict[dn_]:
                pid_ = self.directory_name_dict[dn_][pid_].gdriveid
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
        pid_ = self.get_or_create_directory(dname)
        return self.gdrive.upload(fname, parent_id=pid_)
