#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    extract FileList object for files in onedrive
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .file_list import FileList


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
        raise NotImplementedError

    def append_item(self, item):
        """ append file to FileList, fill dict's """
        raise NotImplementedError

    def append_dir(self, item):
        """ append directory to FileList """
        raise NotImplementedError

    def get_export_path(self, finfo, abspath=True, is_dir=False):
        """ determine export path for given finfo object"""
        raise NotImplementedError

    def fix_export_path(self):
        """ determine export paths for finfo objects in file list"""
        raise NotImplementedError

    def fill_file_list_onedrive(self, number_to_process=-1, searchstr=None,
                              verbose=True):
        """ fill OneDrive file list"""
        raise NotImplementedError

    def get_or_create_directory(self, dname):
        """ create directory on onedrive """
        raise NotImplementedError

    def delete_directory(self, dname):
        """ delete directory on onedrive """
        raise NotImplementedError

    def upload_file(self, fname, pathname=None):
        """ upload file """
        raise NotImplementedError
