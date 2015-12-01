#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    extract FileList object for files in onedrive
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

from sync_app.file_list import FileList
from sync_app.file_info_onedrive import (FileInfoOneDrive, BASE_DIR)


class FileListOneDrive(FileList):
    """ OneDrive File List """

    def __init__(self, filelist=None, basedir=None, onedrive=None):
        """ Init Function """
        FileList.__init__(self, filelist=filelist, basedir=basedir,
                          filelist_type='onedrive')
        self.filelist_id_dict = {}
        self.directory_id_dict = {}
        self.directory_name_dict = {}
        self.onedrive = onedrive

    def __getitem__(self, key):
        for dict_ in (self.filelist_id_dict, self.directory_id_dict,
                      self.directory_name_dict):
            if key in dict_:
                return dict_[key]
        return FileList.__getitem__(self, key)

    def append(self, finfo):
        """ overload FileList.append """
        FileList.append(self, finfo)
        self.filelist_id_dict[finfo.onedriveid] = finfo

    def append_item(self, item):
        """ append file to FileList, fill dict's """
        finfo = FileInfoOneDrive(onedrive=self.onedrive, item=item)

        ### Fix paths
        finfo.exportpath = self.get_export_path(finfo, abspath=False)
        if not finfo.urlname:
            finfo.urlname = 'onedrive://%s' % (finfo.exportpath)
        finfo.filename = '%s/%s' % (finfo.exportpath,
                                    os.path.basename(finfo.filename))

        if finfo.onedriveid in self.filelist_id_dict:
            return finfo
        if finfo.filename in self.filelist_name_dict:
            for ffn in self.filelist_name_dict[finfo.filename]:
                if finfo.sha1sum == ffn.sha1sum:
                    return finfo

        self.append(finfo)
        self.filelist_id_dict[finfo.onedriveid] = finfo
        return finfo

    def append_dir(self, item):
        """ append directory to FileList """
        finfo = FileInfoOneDrive(onedrive=self.onedrive, item=item)
        if 'folder' not in item:
            return finfo

        self.filelist_id_dict[finfo.onedriveid] = finfo
        self.directory_id_dict[finfo.onedriveid] = finfo
        self.directory_name_dict[finfo.filename] = finfo

    def get_export_path(self, finfo, abspath=True, is_dir=False):
        """ determine export path for given finfo object"""
        fullpath = []
        if is_dir:
            fullpath.append(finfo.filename)
        pid = finfo.parentid
        while pid != 'root':
            if pid in self.filelist_id_dict:
                finf = self.filelist_id_dict[pid]
                pid = finf.parentid
                fullpath.append(os.path.basename(finf.filename))
            else:
                raise ValueError('no parent %s' % pid)
        fullpath = '/'.join(fullpath[::-1])
        if not fullpath:
            fullpath = 'OneDrive'
        elif 'OneDrive' not in fullpath:
            fullpath = 'OneDrive/' + fullpath
        fullpath = fullpath.replace('OneDrive', BASE_DIR)
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
        """ fill OneDrive file list"""
        if not self.onedrive:
            raise Exception('what happened?')
        if verbose:
            print('get_folders')
        self.onedrive.number_to_process = -1
        self.onedrive.get_folders(self.append_dir)
        if verbose:
            print('list_files')
        self.onedrive.number_to_process = number_to_process
        self.onedrive.items_processed = 0
        self.onedrive.list_files(self.append_item)
        self.fill_hash_dicts()
        if verbose:
            print('update paths')

    def get_or_create_directory(self, dname):
        """ create directory on onedrive """
        pid_ = 'root'
        dn_list = dname.replace(BASE_DIR + '/', '').split('/')

        if dn_list[0] in self.directory_name_dict:
            pid_ = self.directory_name_dict[dn_list[0]].onedriveid
        else:
            item = self.onedrive.create_directory(dn_list[0], parent_id=pid_)
            self.append_dir(item)
            pid_ = item['id']
        for dn_ in dn_list[1:]:
            if dn_ in self.directory_name_dict \
                    and pid_ == self.directory_name_dict[dn_].parentid:
                pid_ = self.directory_name_dict[dn_].onedriveid
            else:
                item = self.onedrive.create_directory(dn_, parent_id=pid_)
                self.append_dir(item)
                pid_ = item['id']
        return pid_

    def delete_directory(self, dname):
        """ delete directory on onedrive """
        pid = self.get_or_create_directory(dname)
        self.onedrive.delete_file(pid)

    def upload_file(self, fname, pathname=None):
        """ upload file """
        dname = os.path.dirname(fname)
        pid_ = 'root'
        if pathname:
            dname = pathname
            pid_ = self.get_or_create_directory(dname)
        item = self.onedrive.upload(fname, parent_id=pid_)
        item['parentid'] = pid_
        self.append_item(item)
        return item['id']
