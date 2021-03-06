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
import shutil
import unittest

CURDIR = os.path.abspath(os.curdir)
os.sys.path.append(CURDIR)

from sync_app.util import get_md5, get_random_hex_string
from sync_app.file_list_gdrive import FileListGdrive
from sync_app.gdrive_instance import GdriveInstance

TEST_FILE = 'tests/test_dir/hello_world.txt'
TEST_DIR = 'tests/test_dir'
TEST_GDR = 'Amazon-Gift-Card.pdf'

HOMEDIR = os.getenv('HOME')


class TestSyncAppGdrive(unittest.TestCase):
    """ SyncApp Unit Tests """

    def setUp(self):
        self.gdrive = GdriveInstance()
        self.test_title = None

    def test_gdrive_list_files(self):
        """ Test GdriveInstance.list_files """

        def get_title(item):
            """ callback fn """
            self.test_title = item['name']

        self.gdrive.list_files(get_title, searchstr=TEST_GDR)
        md_ = hashlib.md5()
        if hasattr(self.test_title, 'encode'):
            self.test_title = self.test_title.encode()
        md_.update(self.test_title)
        self.assertEqual(md_.hexdigest(), 'ee3ff087897ce88747e7c2b2fc0a59df')

    def test_gdrive_upload_search(self):
        """ Test GdriveInstance.upload """
        flist_gdrive = FileListGdrive(gdrive=self.gdrive)

        flist_gdrive.get_folders()
        flist_gdrive.get_or_create_directory(TEST_DIR)
        test_file = '%s.%06x.txt' % (TEST_FILE, get_random_hex_string(4))
        shutil.copy(TEST_FILE, test_file)
        fid = flist_gdrive.upload_file(test_file)
        sstr = os.path.basename(test_file)
        self.gdrive.list_files(flist_gdrive.append_item, searchstr=sstr)
        #        flist_gdrive.get_folders()
        finf_ = flist_gdrive.filelist_id_dict[fid]
        finf_.download()
        fname = '%s/gDrive/%s' % (HOMEDIR, test_file)

        self.assertEqual(fid, finf_.gdriveid)
        finf_.delete()
        flist_gdrive.delete_directory(TEST_DIR)
        os.remove(test_file)
        self.assertEqual(flist_gdrive.filelist_id_dict[fid].exportpath,
                         '%s/gDrive/%s' % (HOMEDIR, TEST_DIR))
        self.assertEqual(flist_gdrive.filelist_id_dict[fid].md5sum,
                         '8ddd8be4b179a529afa5f2ffae4b9858')
        self.assertEqual(get_md5(fname), '8ddd8be4b179a529afa5f2ffae4b9858')
        os.remove(fname)

    def test_gdrive_search_directory(self):
        """ Test FileListGdrive """
        flist_gdrive = FileListGdrive(gdrive=self.gdrive)
        flist_gdrive.get_folders()
        flist_gdrive.fix_export_path()
        id_ = flist_gdrive.directory_name_dict['share'][0].gdriveid
        val = flist_gdrive.directory_id_dict[id_]
        self.assertEqual(val.exportpath,
                         '%s/gDrive/ATLAS/code/' % HOMEDIR + 'ISF_Calo_Validation/17.2.4.10')

    def test_gdrive_list_directories(self):
        """ Test FileListGdrive """
        flist_gdrive = FileListGdrive(gdrive=self.gdrive)
        flist_gdrive.get_folders()
        flist_gdrive.fix_export_path()

        finf_ = flist_gdrive.directory_name_dict['share'][0]

        self.assertEqual(finf_.exportpath,
                         '%s/gDrive/ATLAS/code/' % HOMEDIR + 'ISF_Calo_Validation/17.2.4.10')

    def test_gdrive_create_directory(self):
        """ Test GdriveInstance.insert """
        body_obj = {'name': 'test_directory', 'mimeType': 'application/vnd.google-apps.folder'}
        request = self.gdrive.gfiles.create(body=body_obj)
        response = request.execute()
        flist_gdrive = FileListGdrive(gdrive=self.gdrive)
        flist_gdrive.get_folders()
        flist_gdrive.fix_export_path()
        fid = response['id']
        self.gdrive.delete_file(fid)
        self.assertEqual('test_directory', flist_gdrive.filelist_id_dict[fid].filename)


if __name__ == '__main__':
    unittest.main()
