#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    extract FileList object for files in box
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

from sync_app.file_list import FileList
from sync_app.file_info_box import (FileInfoBox, BASE_DIR)


class FileListBox(FileList):
    """ Box File List """

    def __init__(self, filelist=None, basedir=None, box=None):
        """ Init Function """
        FileList.__init__(self, filelist=filelist, basedir=basedir,
                          filelist_type='box')
        self.filelist_id_dict = {}
        self.directory_id_dict = {}
        self.directory_name_dict = {}
        self.box = box

    def __getitem__(self, key):
        for dict_ in (self.filelist_id_dict, self.directory_id_dict,
                      self.directory_name_dict):
            if key in dict_:
                return dict_[key]
        return FileList.__getitem__(self, key)

    def append(self, finfo):
        """ overload FileList.append """
        FileList.append(self, finfo)
        self.filelist_id_dict[finfo.boxid] = finfo

    def append_item(self, item):
        """ append file to FileList, fill dict's """
        finfo = FileInfoBox(box=self.box, item=item)

        ### Fix paths
        finfo.exportpath = self.get_export_path(finfo, abspath=False)
        if not finfo.urlname:
            finfo.urlname = 'box://%s' % (finfo.exportpath)
        finfo.filename = '%s/%s' % (finfo.exportpath,
                                    os.path.basename(finfo.filename))

        if finfo.boxid in self.filelist_id_dict:
            return finfo
        if finfo.filename in self.filelist_name_dict:
            for ffn in self.filelist_name_dict[finfo.filename]:
                if finfo.sha1sum == ffn.sha1sum:
                    return finfo

        self.append(finfo)
        self.filelist_id_dict[finfo.boxid] = finfo
        return finfo

    def append_dir(self, item):
        """ append directory to FileList """
        finfo = FileInfoBox(box=self.box, item=item)
        if item.get('type') != 'folder':
            return finfo

        self.filelist_id_dict[finfo.boxid] = finfo
        self.directory_id_dict[finfo.boxid] = finfo
        self.directory_name_dict[finfo.filename] = finfo

    def get_export_path(self, finfo, abspath=True, is_dir=False):
        """ determine export path for given finfo object"""
        fullpath = []
        if is_dir:
            fullpath.append(finfo.filename)
        pid = finfo.parentid
        while pid != '0':
            if pid in self.filelist_id_dict:
                finf = self.filelist_id_dict[pid]
                pid = finf.parentid
                fullpath.append(os.path.basename(finf.filename))
            else:
                raise ValueError('no parent %s' % pid)
        fullpath = '/'.join(fullpath[::-1])
        if not fullpath:
            fullpath = 'Box'
        elif 'Box' not in fullpath:
            fullpath = 'Box/' + fullpath
        fullpath = fullpath.replace('Box', BASE_DIR)
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
        """ fill Box file list"""
        if not self.box:
            raise Exception('what happened?')
        if verbose:
            print('get_folders')
        self.box.number_to_process = -1
        self.box.get_folders(self.append_dir)
        if verbose:
            print('list_files')
        self.box.number_to_process = number_to_process
        self.box.items_processed = 0
        self.box.list_files(self.append_item)
        self.fill_hash_dicts()
        if verbose:
            print('update paths')

    def get_or_create_directory(self, dname):
        """ create directory on box """
        pid_ = '0'
        dn_list = dname.replace(BASE_DIR + '/', '').split('/')

        if dn_list[0] in self.directory_name_dict:
            pid_ = self.directory_name_dict[dn_list[0]].boxid
        else:
            item = self.box.create_directory(dn_list[0], parent_id=pid_)
            self.append_dir(item)
            pid_ = item['id']
        for dn_ in dn_list[1:]:
            if dn_ in self.directory_name_dict \
                    and pid_ == self.directory_name_dict[dn_].parentid:
                pid_ = self.directory_name_dict[dn_].boxid
            else:
                item = self.box.create_directory(dn_, parent_id=pid_)
                self.append_dir(item)
                pid_ = item['id']
        return pid_

    def delete_directory(self, dname):
        """ delete directory on box """
        pid = self.get_or_create_directory(dname)
        self.box.delete_directory(pid)

    def upload_file(self, fname, pathname=None):
        """ upload file """
        dname = os.path.dirname(fname)
        pid_ = '0'
        if pathname:
            dname = pathname
            pid_ = self.get_or_create_directory(dname)
        item = self.box.upload(fname, parent_id=pid_)
        item['parentid'] = pid_
        self.append_item(item)
        return item['id']
