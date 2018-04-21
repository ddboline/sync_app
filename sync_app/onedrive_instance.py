#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Class to interface with MSFT OneDrive api
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import time
from onedrivesdk import get_default_client, Folder, Item, error
try:
    import cPickle as pickle
except ImportError:
    import pickle

from sync_app.get_auth_code_server import get_auth_code
from sync_app.util import HOMEDIR


def t_get(request):
    timeout = 1
    while True:
        try:
            return request.get()
        except Exception as exc:
            print('timeout %s, %s' % (timeout, exc))
            time.sleep(timeout)
            timeout *= 2
            if timeout >= 64:
                raise


class OneDriveInstance(object):
    """ class to make use of google python api """

    def __init__(self, number_to_process=-1):
        """ init function """
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

    def read_credentials(self, credential_file=HOMEDIR + '/.onedrive/credentials'):
        """ read credentials from file """
        with open(credential_file, 'r') as credfile:
            for line in credfile:
                key_, val_ = line.split()[:2]
                for key in ('redirect_uri', 'client_id', 'client_secret'):
                    if key.lower() == key_.strip().lower():
                        setattr(self, key, val_)

    def get_auth(self):
        """ do authorization """
        self.client = get_default_client(
            client_id=self.client_id,
            scopes=['wl.signin', 'wl.offline_access', 'onedrive.readwrite'])
        if os.path.exists(os.path.join(HOMEDIR, '.onedrive_session.pkl')):
            with open(os.path.join(HOMEDIR, '.onedrive_session.pkl'), 'rb') as pfile:
                self.client.auth_provider._session = pickle.load(pfile)
        else:
            auth_url = \
                self.client.auth_provider.get_auth_url(self.redirect_uri)
            code = get_auth_code(auth_url, self.redirect_uri)
            self.client.auth_provider.authenticate(code, self.redirect_uri, self.client_secret)
            with open(os.path.join(HOMEDIR, '.onedrive_session.pkl'), 'wb') as pfile:
                pickle.dump(
                    self.client.auth_provider._session, pfile, protocol=pickle.HIGHEST_PROTOCOL)

        return self.client

    def list_files(self, callback_fn):
        """ list non-directory files """

        def walk_nodes(parentid='root'):
            parent_node = self.client.item(id=parentid)
            for node in t_get(parent_node.children):
                item = node.to_dict()
                item['parentid'] = parentid
                if 'folder' in item and item['folder']['childCount'] > 0:
                    walk_nodes(parentid=item['id'])
                else:
                    callback_fn(item)

        walk_nodes(parentid='root')

    def get_folders(self, callback_fn):
        """ get folders """

        def walk_nodes(parentid='root'):
            parent_node = self.client.item(id=parentid)
            for node in t_get(parent_node.children):
                item = node.to_dict()
                item['parentid'] = parentid
                if 'folder' in item:
                    callback_fn(item)
                    if item['folder']['childCount'] > 0:
                        walk_nodes(parentid=item['id'])

        walk_nodes(parentid='root')

    def download(self, did, exportfile, sha1sum=None):
        """ download using dlink url """
        dirname = os.path.dirname(exportfile)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        self.client.item(id=did).download(exportfile + '.new')
        if sha1sum:
            from sync_app.util import get_sha1
            sha = get_sha1(exportfile + '.new')
            if sha != sha1sum:
                raise TypeError('%s %s' % (sha, sha1sum))
        os.rename('%s.new' % exportfile, exportfile)
        return True

    def upload(self, fname, parent_id='root'):
        """ upload fname and assign parent_id if provided """
        bname = os.path.basename(fname)
        node = self.client.item(drive="me", id=parent_id)
        return node.children[bname].upload(fname).to_dict()

    def create_directory(self, dname, parent_id='root'):
        """ create directory, assign parent_id if supplied """
        if not parent_id:
            raise ValueError('need to specify parent_id')
        if dname == '':
            result = t_get(self.client.item(id='root')).to_dict()
            result['parentid'] = 'root'
            return result
        newfolder = Folder()
        newitem = Item()
        newitem.name = dname
        newitem.folder = newfolder

        try:
            tmp = self.client.item(id=parent_id).children.add(newitem)
        except error.OneDriveError as exc:
            raise
        result = tmp.to_dict()
        result['parentid'] = parent_id
        return result

    def delete_file(self, fileid):
        """ delete file by fileid """
        return self.client.item(id=fileid).delete()
