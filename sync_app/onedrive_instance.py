#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Class to interface with MSFT OneDrive api
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from onedrivesdk import get_default_client
from onedrivesdk.helpers import GetAuthCodeServer
from onedrivesdk.request.one_drive_client import OneDriveClient

from .util import HOMEDIR


class OneDriveInstance(object):
    """ class to make use of google python api """

    def __init__(self, client=None, number_to_process=-1):
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

        if isinstance(client, OneDriveClient):
            self.client = client
        else:
            self.client = self.get_auth()

    def read_credentials(self,
                         credential_file=HOMEDIR+'/.onedrive/credentials'):
        """ read credentials from file """
        with open(credential_file, 'r') as credfile:
            for line in credfile:
                key_, val_ = line.split()[:2]
                for key in ('redirect_uri', 'client_id', 'client_secret'):
                    if key.lower() == key_.strip().lower():
                        setattr(self, key, val_)

    def get_auth(self):
        """ do authorization """
        client = get_default_client(client_id=self.client_id,
                                    scopes=['wl.signin',
                                            'wl.offline_access',
                                            'onedrive.readwrite'])
        auth_url = client.auth_provider.get_auth_url(self.redirect_uri)
        code = GetAuthCodeServer.get_auth_code(auth_url, self.redirect_uri)

        client.auth_provider.authenticate(code, self.redirect_uri,
                                          self.client_secret)
        return client

    def process_response(self, response, callback_fn=None):
        """ callback_fn applied to each item returned by response """
        raise NotImplementedError

    def process_request(self, request, callback_fn=None):
        """ call process_response until new_request exists or until stopped """
        raise NotImplementedError

    def list_files(self, callback_fn, searchstr=None):
        """ list non-directory files """
        raise NotImplementedError

    def get_folders(self, callback_fn):
        """ get folders """
        raise NotImplementedError

    def download(self, dlink, exportfile, md5sum=None):
        """ download using dlink url """
        raise NotImplementedError

    def upload(self, fname, parent_id=None):
        """ upload fname and assign parent_id if provided """
        raise NotImplementedError

    def set_parent_id(self, fid, parent_id):
        """ set parent_id """
        raise NotImplementedError

    def create_directory(self, dname, parent_id=None):
        """ create directory, assign parent_id if supplied """
        raise NotImplementedError

    def delete_file(self, fileid):
        """ delete file by fileid """
        raise NotImplementedError

    def get_parents(self, fids=None):
        """ get parents of files by fileid """
        raise NotImplementedError


def test_gdrivce_instance():
    """ test OneDriveInstance """
    assert True
