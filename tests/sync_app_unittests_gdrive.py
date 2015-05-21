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

from sync_app.sync_utils import get_md5
from sync_app.file_list_gdrive import FileListGdrive
from sync_app.gdrive_instance import GdriveInstance

TEST_FILE = 'tests/test_dir/hello_world.txt'
TEST_DIR = 'tests/test_dir'
TEST_GDR = 'Amazon-Gift-Card.pdf'

class TestSyncApp(unittest.TestCase):
    """ SyncApp Unit Tests """

    def test_gdrive_list_files(self):
        """ Test GdriveInstance.list_files """
        self.test_title = None
        def get_title(item):
            self.test_title = item['title']
        gdrive = GdriveInstance(number_to_process=10)
        gdrive.list_files(get_title, searchstr=TEST_GDR)
        m = hashlib.md5()
        m.update(self.test_title)
        self.assertEqual(m.hexdigest(), 'ee3ff087897ce88747e7c2b2fc0a59df')

    def test_gdrive_upload_search_download_delete(self):
        """ Test GdriveInstance.upload """
        gdrive = GdriveInstance()
        flist_gdrive = FileListGdrive(gdrive=gdrive)

        gdrive.get_folders(flist_gdrive.append_dir)

        flist_gdrive.create_directory(os.path.dirname(TEST_FILE))
        fid = flist_gdrive.upload_file(TEST_FILE)
        sstr = os.path.basename(TEST_FILE)
        gdrive.list_files(flist_gdrive.append_item, searchstr=sstr)
        gdrive.get_folders(flist_gdrive.append_dir)

        flist_gdrive.filelist_id_dict[fid].download()
        fname = '/home/ddboline/gDrive/tests/test_dir/hello_world.txt'

        gdrive.delete_file(fid)
        flist_gdrive.delete_directory(os.path.dirname(TEST_FILE))
        self.assertEqual(flist_gdrive.filelist_id_dict[fid].exportpath,
                         '/home/ddboline/gDrive/tests/test_dir')
        self.assertEqual(flist_gdrive.filelist_id_dict[fid].md5sum,
                         '8ddd8be4b179a529afa5f2ffae4b9858')
        self.assertEqual(get_md5(fname), '8ddd8be4b179a529afa5f2ffae4b9858')
        os.remove(fname)

    def test_gdrive_search_directory(self):
        """ Test FileListGdrive """
        gdrive = GdriveInstance()
        flist_gdrive = FileListGdrive()
        gdrive.get_folders(flist_gdrive.append_dir)
        flist_gdrive.fix_export_path()
        id_ = flist_gdrive.directory_name_dict['share'].gdriveid
        val = flist_gdrive.directory_id_dict[id_]
        self.assertEqual(val.exportpath,
                         '/home/ddboline/gDrive/ATLAS/code/' +
                         'ISF_Calo_Validation/17.2.4.10')

    def test_gdrive_list_directories(self):
        """ Test FileListGdrive """
        gdrive = GdriveInstance()
        flist_gdrive = FileListGdrive(gdrive=gdrive)
        gdrive.get_folders(flist_gdrive.append_dir)
        flist_gdrive.fix_export_path()

        finf_ = flist_gdrive.directory_name_dict['share']

        self.assertEqual(finf_.exportpath,
                         '/home/ddboline/gDrive/ATLAS/code/' +
                         'ISF_Calo_Validation/17.2.4.10')

    def test_gdrive_create_directory(self):
        """ Test GdriveInstance.insert """
        gdrive = GdriveInstance()
        body_obj = {'title': 'test_directory',
                    'mimeType': 'application/vnd.google-apps.folder'}
        request = gdrive.service.files().insert(body=body_obj)
        response = request.execute()
        flist_gdrive = FileListGdrive()
        gdrive.get_folders(flist_gdrive.append_dir)
        flist_gdrive.fix_export_path()
        fid = response['id']
        gdrive.delete_file(fid)
        self.assertEqual('test_directory',
                         flist_gdrive.filelist_id_dict[fid].filename)


if __name__ == '__main__':
    unittest.main()
