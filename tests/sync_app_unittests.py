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

from sync_app.file_cache import FileListCache
from sync_app.file_list_local import FileInfoLocal, FileListLocal
#from sync_app.file_list_gdrive import FileInfoGdrive
from sync_app.file_list_gdrive import FileListGdrive
from sync_app.gdrive_instance import GdriveInstance

TEST_FILE = 'tests/test_dir/hello_world.txt'
TEST_DIR = 'tests/test_dir'
TEST_GDR = 'Amazon-Gift-Card.pdf'

class TestSyncApp(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        if os.path.exists('.tmp_file_list_cache.pkl.gz'):
            os.remove('.tmp_file_list_cache.pkl.gz')
        pass

    def test_file_info_local(self):
        finfo = FileInfoLocal(fn=TEST_FILE)
        output = ('%s' % finfo).replace(CURDIR, '')
#        print('finfo', output)
        m = hashlib.md5()
        m.update(output)
        self.assertEqual(m.hexdigest(), 'bb0681fe01c42429d0a7b0994f0d9265')

    def test_file_list_local(self):
        flist = FileListLocal()
        flist.fill_file_list_local(directory=TEST_DIR)
        output = []
        for fl in flist.filelist:
            output.append(('%s' % fl).replace(CURDIR, ''))
        output = sorted(output)
#        print('file_list', '\n'.join(output))
        m = hashlib.md5()
        for out in sorted(output):
            m.update(out)
        self.assertEqual(m.hexdigest(), '30eceb5a3d7b9c761651f8b1df5e53b5')

    def test_file_list_cache(self):
        flist = FileListLocal()
        flist.fill_file_list_local(directory=TEST_DIR)
        fcache = FileListCache(pickle_file='.tmp_file_list_cache.pkl.gz')
        fcache.write_cache_file_list(flist.filelist)
        del flist
        flist = fcache.get_cache_file_list()
        output = []
        for fl in flist.filelist:
            output.append(('%s' % fl).replace(CURDIR, ''))
        output = sorted(output)
#        print('file_cache', '\n'.join(output))
        m = hashlib.md5()
        for out in sorted(output):
            m.update(out)
        self.assertEqual(m.hexdigest(), '30eceb5a3d7b9c761651f8b1df5e53b5')

    def test_gdrive_list_files(self):
        self.test_title = None
        def get_title(item):
            self.test_title = item['title']
        gdrive = GdriveInstance(number_to_process=10)
        gdrive.list_files(get_title, searchstr=TEST_GDR)
        m = hashlib.md5()
        m.update(self.test_title)
        self.assertEqual(m.hexdigest(), 'ee3ff087897ce88747e7c2b2fc0a59df')

    def test_gdrive_upload_search_delete(self):
        self.test_title = None
        self.test_id = None
        def get_id(item):
            self.test_title = item['title']
            self.test_id= item['id']
        gdrive = GdriveInstance(number_to_process=10)
        gdrive.upload(TEST_FILE)

        gdrive.list_files(get_id,
                               searchstr=os.path.basename(TEST_FILE))

        gdrive.delete_file(self.test_id)
        print(self.test_id, self.test_title)

    def test_gdrive_search_directory(self):
        test_dirs = {}
        test_ids = {}
        def get_id(item):
            test_dirs[item['title']] = item['id']
            test_ids[item['id']] = item['title']
        gdrive = GdriveInstance()
        gdrive.get_folders(get_id)
        parents = gdrive.get_parents([test_dirs['share']])
        for parent in parents:
#            print('parent', parent)
            if parent['id'] in test_ids:
                print('parent', test_ids[parent['id']])

    def test_gdrive_list_directories(self):
        gdrive = GdriveInstance()
        flist_gdrive = FileListGdrive()
        gdrive.get_folders(flist_gdrive.append_dir)
        flist_gdrive.fix_export_path()
        expath_ = flist_gdrive.directory_name_dict['share'].exportpath
        self.assertEqual(expath_, 
                         '/home/ddboline/gDrive/ATLAS/code/' + 
                         'ISF_Calo_Validation/17.2.4.10')

    def test_gdrive_create_directory(self):
        gdrive = GdriveInstance(number_to_process=10)
        body_obj = {'title': 'tests',
                    'mimeType': 'application/vnd.google-apps.folder'}
        request = gdrive.service.files().insert(body=body_obj)
        response = request.execute()
        print(response)

if __name__ == '__main__':
    unittest.main()
