#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Class to interface with BOX api
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
from boxsdk import OAuth2, Client
from boxsdk.exception import BoxAPIException
#from boxsdk import get_default_client, Folder, Item
from sync_app.get_auth_code_server import get_auth_code
try:
    import cPickle as pickle
except ImportError:
    import pickle

from sync_app.util import HOMEDIR


class BoxInstance(object):
    """ class to make use of google python api """

    def __init__(self, number_to_process=-1,
                 credential_file=HOMEDIR+'/.box/credentials'):
        """ init function """
        self.credential_file = credential_file
        self.redirect_uri = ''
        self.client_id = ''
        self.client_secret = ''
        self.list_of_keys = {}
        self.list_of_mimetypes = {}
        self.items_processed = 0
        self.list_of_folders = {}
        self.list_of_items = {}
        self.number_to_process = number_to_process
        self.read_credentials()
        self.client = self.get_auth()

    def store_tokens(self, access_token, refresh_token):
        with open('.box_tokens.pkl', 'w') as credfile:
            tmp = (access_token, refresh_token)
            pickle.dump(obj=tmp, file=credfile, protocol=-1)

    def read_credentials(self,
                         credential_file=HOMEDIR+'/.box/credentials'):
        """ read credentials from file """
        with open(credential_file, 'r') as credfile:
            for line in credfile:
                key_, val_ = line.split()[:2]
                for key in ('redirect_uri', 'client_id', 'client_secret'):
                    if key.lower() == key_.strip().lower():
                        setattr(self, key, val_)

    def get_auth(self):
        """ do authorization """
        if os.path.exists('.box_tokens.pkl'):
            with open('.box_tokens.pkl', 'rb') as pfile:
                self.access_token, self.refresh_token = pickle.load(pfile)
                self.oauth = OAuth2(client_id=self.client_id,
                                    client_secret=self.client_secret,
                                    store_tokens=self.store_tokens,
                                    access_token=self.access_token,
                                    refresh_token=self.refresh_token)
        else:
            self.oauth = OAuth2(client_id=self.client_id,
                                client_secret=self.client_secret,
                                store_tokens=self.store_tokens)
            auth_url, csrf_token = self.oauth.get_authorization_url(
                self.redirect_uri)
            code = get_auth_code(auth_url, self.redirect_uri)
            print(code)
            self.access_token, self.refresh_token = \
                self.oauth.authenticate(code)

        self.client = Client(self.oauth)

        return self.client

    def list_files(self, callback_fn):
        """ list non-directory files """
        fields = ['id', 'size', 'etag', 'description', 'parent', 'name', 'type', 'modified_at', 'sha1']
        def walk_nodes(parentid='0'):
            parent_node = self.client.folder(folder_id=parentid).get()
            cur_offset = 0
            while True:
                new_items = parent_node.get_items(limit=100, offset=cur_offset, fields=fields)
                if not new_items:
                    break
                for item in new_items:
                    item = item._response_object
                    item['parentid'] = parentid
                    if item.get('type', '') == 'folder':
                        walk_nodes(parentid=item['id'])
                    else:
                        callback_fn(item)
                print(cur_offset)
                cur_offset += 100
        walk_nodes(parentid='0')

    def get_folders(self, callback_fn):
        """ get folders """
        def walk_nodes(parentid='0'):
            parent_node = self.client.folder(folder_id=parentid).get()
            item_col = parent_node._response_object.get('item_collection', {})
            entries = item_col.get('entries', [])
            for item in entries:
                item['parentid'] = parentid
                if item.get('type', '') == 'folder':
                    node = self.client.folder(folder_id=item['id']).get()
                    node = node._response_object
                    node['parentid'] = item['parentid']
                    callback_fn(node)
                    walk_nodes(parentid=item['id'])
        walk_nodes(parentid='0')

    def download(self, did, exportfile, sha1sum=None):
        """ download using dlink url """
        dirname = os.path.dirname(os.path.abspath(exportfile))
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(exportfile + '.new', 'w') as outfile:
            self.client.file(file_id=did).download_to(outfile)
        if sha1sum:
            from sync_app.util import get_sha1
            sha = get_sha1(exportfile + '.new')
            if sha != sha1sum:
                raise TypeError('%s %s' % (sha, sha1sum))
        os.rename('%s.new' % exportfile, exportfile)
        return True

    def upload(self, fname, parent_id='0'):
        """ upload fname and assign parent_id if provided """
        bname = os.path.basename(fname)
        parent = self.client.folder(folder_id=parent_id)
        try:
            file_obj = parent.upload(file_path=fname, file_name=bname).get()
        except BoxAPIException as exc:
            print('BoxAPIException %s' % exc)
            raise
        item = file_obj._response_object
        item['parentid'] = parent_id
        return item

    def create_directory(self, dname, parent_id='0'):
        """ create directory, assign parent_id if supplied """
        if not parent_id:
            raise ValueError('need to specify parent_id')
        parent = self.client.folder(folder_id=parent_id)
        try:
            parent.create_subfolder(dname)
        except BoxAPIException as exc:
            print('BoxAPIException %s' % exc)
            pass
        parent = parent.get()
        item = parent._response_object
        items = item.get('item_collection', {}).get('entries', [])
        for item in items:
            if item['type'] == 'folder' and item['name'] == dname:
                item['parentid'] = parent_id
                return item

    def delete_directory(self, dirid):
        """ delete directory by folderid """
        return self.client.folder(folder_id=dirid).delete()

    def delete_file(self, fileid):
        """ delete file by fileid """
        return self.client.file(file_id=fileid).delete()


def test_box_instance():
    box = BoxInstance()
    box.get_folders(lambda x: print(x))
    box.list_files(lambda x: print(x))
    newdir = box.create_directory('test')
    item = box.upload(fname='tests/test_dir/hello_world.txt',
                      parent_id=newdir['id'])
    box.download(did=item['id'], exportfile='test.txt')
    result = box.delete_file(fileid=item['id'])
    assert result is True
    result = box.delete_directory(dirid=newdir['id'])
    assert result is True
