#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Class to interface with google drive api
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os, time
from apiclient import sample_tools
from apiclient.errors import HttpError

class GdriveInstance(object):
    """ class to make use of google python api """

    def __init__(self, app='drive', version='v2', number_to_process=-1):
        """ init function """

        self.list_of_keys = {}
        self.list_of_mimetypes = {}
        self.items_processed = 0
        self.list_of_folders = {}
        self.list_of_items = {}

        self.service, self.flags = \
            sample_tools.init([], app, version, __doc__, __file__,\
                scope='https://www.googleapis.com/auth/%s' % app)
        self.number_to_process = number_to_process

    def process_response(self, response, callback_fn=None):
        """ callback_fn needs to be supplied to process each item """
        if not callback_fn:
            return 0
        for item in response['items']:
            if self.number_to_process > 0\
                    and self.items_processed > self.number_to_process:
                return 0
            if callback_fn:
                callback_fn(item)
            self.items_processed += 1

    def process_request(self, request, callback_fn=None):
        response = request.execute()

        new_request = True
        while new_request:
            if self.process_response(response, callback_fn) == 0:
                return

            new_request = self.service.files().list_next(request, response)
            if not new_request:
                return
            request = new_request
            try:
                response = request.execute()
            except HttpError:
                time.sleep(5)
                response = request.execute()

    def list_files(self, callback_fn, searchstr=None):
        query_string = 'mimeType != "application/vnd.google-apps.folder"'
        if searchstr:
            query_string += ' and title contains "%s"' % searchstr
        request = self.service.files().list(q=query_string)
        self.process_request(request, callback_fn)

    def download(self, dlink, exportfile):
        dirname = os.path.dirname(exportfile)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        resp, furl = self.service._http.request(dlink)
        if resp['status'] != '200':
            print(dlink)
            print('something bad happened %s' % resp)
            return False
        with open(exportfile, 'wb') as outfile:
            for line in furl:
                outfile.write(line)
        return True

    def upload(self, fname):
        parent_id = None

        fn_ = os.path.basename(fname)
#        base_dir = '/home/ddboline/gDrive/'
#        directories = fname.replace(base_dir, '').split('/')

        body_obj = {'title': fn_,}

        request = self.service.files().insert(body=body_obj, media_body=fname)
        response = request.execute()

        fid = response['id']

        request = self.service.parents().list(fileId=fid)
        response = request.execute()

        current_pid = response['items'][0]['id']

        request = self.service.files().update(fileId=fid,
                                              addParents=parent_id,
                                              removeParents=current_pid)
        response = request.execute()

    def delete_file(self, fileid):
        request = self.service.files().delete(fileId=fileid)
        response = request.execute()
        return response

    def get_folders(self, callback_fn):
        searchstr = 'mimeType = "application/vnd.google-apps.folder"'
        request = self.service.files().list(q=searchstr)
        self.process_request(request, callback_fn)

    def get_parents(self, fids=None):
        """ function to list files in drive """
        if not fids:
            return
        parents_output = []
        for fid in fids:
            request = self.service.files().get(fileId=fid)
            response = request.execute()
            parents_output.extend(response['parents'])
        return parents_output
