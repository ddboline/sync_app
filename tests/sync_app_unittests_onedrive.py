#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Unit tests for sync_app
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import hashlib
import unittest

CURDIR = os.path.abspath(os.curdir)
os.sys.path.append(CURDIR)

from sync_app.util import get_sha1
from sync_app.file_list_onedrive import FileListOneDrive
from sync_app.onedrive_instance import OneDriveInstance

TEST_FILE = 'tests/test_dir/hello_world.txt'
TEST_DIR = 'tests/test_dir'
TEST_GDR = 'LettreInv_short_2012.Family.docx'

HOMEDIR = os.getenv('HOME')


class TestSyncAppOneDrive(unittest.TestCase):
    """ SyncApp Unit Tests """

    def setUp(self):
        self.onedrive = OneDriveInstance()
        self.test_title = None

    def test_onedrive_list_files(self):
        """ Test OneDriveInstance.list_files """
        def get_title(item):
            """ callback fn """
            if TEST_GDR in item['name']:
                self.test_title = item['name']
        self.onedrive.list_files(get_title)
        print(dir(self.onedrive.client.auth_provider))
        md_ = hashlib.md5()
        if hasattr(self.test_title, 'encode'):
            self.test_title = self.test_title.encode()
        md_.update(self.test_title)
        self.assertEqual(md_.hexdigest(), 'c95649dad551181f9016881db3510aef')

    def test_onedrive_upload_search(self):
        """ Test OneDriveInstance.upload """
        flist_onedrive = FileListOneDrive(onedrive=self.onedrive)

        self.onedrive.get_folders(flist_onedrive.append_dir)
        self.onedrive.list_files(flist_onedrive.append_item)

        for directory, finfo in flist_onedrive.directory_name_dict.items():
            print(directory)
            print(flist_onedrive.get_export_path(finfo))

        flist_onedrive.get_or_create_directory(os.path.dirname(TEST_FILE))
        fid = flist_onedrive.upload_file(TEST_FILE)
        print(fid)

        finf_ = flist_onedrive.filelist_id_dict[fid]
        finf_.download()

        fname = '%s/OneDrive/%s' % (HOMEDIR, TEST_FILE)

        self.assertEqual(fid, finf_.onedriveid)

        finf_.delete()
        flist_onedrive.delete_directory(os.path.dirname(TEST_FILE))

        self.assertEqual(flist_onedrive.filelist_id_dict[fid].exportpath,
                         '%s/OneDrive/%s' % (HOMEDIR, TEST_DIR))
        self.assertEqual(flist_onedrive.filelist_id_dict[fid].sha1sum,
                         'a0b65939670bc2c010f4d5d6a0b3e4e4590fb92b')
        self.assertEqual(get_sha1(fname),
                         'a0b65939670bc2c010f4d5d6a0b3e4e4590fb92b')
        os.remove(fname)

    def test_onedrive_search_directory(self):
        """ Test FileListOneDrive """
        self.onedrive = OneDriveInstance()
        flist_onedrive = FileListOneDrive()
        self.onedrive.get_folders(flist_onedrive.append_dir)
        flist_onedrive.fix_export_path()
        print(flist_onedrive.directory_name_dict)
        id_ = flist_onedrive.directory_name_dict['Imported'].onedriveid
        val = flist_onedrive.directory_id_dict[id_]
        print(val)
        self.assertEqual(val.exportpath, '%s/OneDrive/Documents' % HOMEDIR)

    def test_onedrive_list_directories(self):
        """ Test FileListOneDrive """
        flist_onedrive = FileListOneDrive(onedrive=self.onedrive)
        self.onedrive.get_folders(flist_onedrive.append_dir)
        flist_onedrive.fix_export_path()

        finf_ = flist_onedrive.directory_name_dict['Imported']

        self.assertEqual(finf_.exportpath, '%s/OneDrive/Documents' % HOMEDIR)


if __name__ == '__main__':
    unittest.main()
