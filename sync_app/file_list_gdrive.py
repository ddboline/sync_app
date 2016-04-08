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
        self.directory_name_dict = defaultdict(list)
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
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            return self.append_dir(item)
        finfo = FileInfoGdrive(gdrive=self.gdrive, item=item)

        root_dir_ = self.get_parent_directories(finfo)
        if not self.root_directory:
            self.root_directory = root_dir_

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

        if finfo.filename in self.filelist:
            finf_ = self.filelist[finfo.filename]
            if finf_.md5sum == finfo.md5sum:
                print(finfo.filename)
                finfo.delete()
            else:
                print(finfo.mimetype)
                print(self.filelist[finfo.filename].mimetype)
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
        self.directory_name_dict[finfo.filename].append(finfo)
        return finfo

    def get_parent_directories(self, finfo):
        pid = finfo.parentid
        while pid is not None:
            newfinfo = self.filelist_id_dict.get(pid, None)
            if newfinfo is None:
                response = self.gdrive.get_file(pid)
                finfo = self.append_item(response)
                pid = finfo.parentid
            else:
                finfo = newfinfo
                pid = finfo.parentid
        return finfo

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
                response = self.gdrive.get_file(pid)
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

    def get_folders(self):
        self.gdrive.get_folders(self.append_dir)
        finfo = self.filelist_id_dict.values()[0]
        self.root_directory = self.get_parent_directories(finfo)

    def fill_file_list(self, number_to_process=-1, searchstr=None,
                       verbose=True):
        """ fill GDrive file list"""
        if not self.gdrive:
            self.gdrive = GdriveInstance()
        if verbose:
            print('get_folders')
        self.gdrive.number_to_process = -1
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
            pid_ = self.root_directory.gdriveid
        else:
            print('no root directory', dname, self.directory_name_dict.keys())

        dn_list = dname.replace(BASE_DIR, 'My Drive').split('/')

        if dn_list[0] != 'My Drive':
            dn_list.insert(0, 'My Drive')
        assert dn_list[0] == 'My Drive'
        assert pid_ is not None

        for dn_ in dn_list[1:]:
            new_pid_ = None
            for item in self.directory_name_dict.get(dn_, []):
                if item.parentid == pid_:
                    new_pid_ = item.gdriveid
                    break
            if new_pid_:
                pid_ = new_pid_
                continue
            item = self.gdrive.create_directory(dn_, parent_id=pid_)
            finf = self.append_dir(item)
            pid_ = finf.gdriveid
            print('create directory %s %s' % (dn_, pid_))
        return pid_

    def delete_directory(self, dname):
        """ delete directory on gdrive """
        pid_ = None
        if self.root_directory:
            pid_ = self.root_directory.gdriveid
        else:
            print('no root directory', dname, self.directory_name_dict.keys())

        dn_list = dname.replace(BASE_DIR, 'My Drive').split('/')

        if dn_list[0] != 'My Drive':
            dn_list.insert(0, 'My Drive')
        assert dn_list[0] == 'My Drive'
        assert pid_ is not None

        for dn_ in dn_list[1:]:
            new_pid_ = None
            for item in self.directory_name_dict.get(dn_, []):
                if item.parentid == pid_:
                    new_pid_ = item.gdriveid
                    break
            if new_pid_:
                pid_ = new_pid_
                continue
        self.gdrive.delete_file(pid_)
        return ''

    def upload_file(self, fname, pathname=None):
        """ upload file """
        if fname in self.filelist:
            return self.filelist[fname]
        dname = os.path.dirname(fname)
        if pathname:
            dname = pathname
        pid_ = self.get_or_create_directory(dname)
        return self.gdrive.upload(fname, parent_id=pid_)
