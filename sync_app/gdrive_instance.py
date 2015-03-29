#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    Class to interface with google drive api
'''
import os, time
from urllib2 import urlopen
from apiclient import sample_tools

import dateutil.parser


class GdriveInstance(object):
    """ class to make use of google python api """

    def __init__(self, app='drive', version='v2', number_to_process=-1):
        """ init function """

        self.list_of_keys = {}
        self.list_of_mimetypes = {}
        self.items_processed = 0
        self.list_of_folders = {}
        self.list_of_items = {}

        curdir = os.curdir

        self.service, self.flags = \
            sample_tools.init([], app, version, __doc__, __file__,\
                scope='https://www.googleapis.com/auth/%s' % app)
        self.number_to_process = number_to_process

    def process_response(self, response, callback_fn=None):
        ''' callback_fn needs to be supplied to process each item '''
        if not callback_fn:
            return 0
        for item in response['items']:
            if self.number_to_process > 0 and self.items_processed > self.number_to_process:
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
            except apiclient.errors.HttpError:
                time.sleep(5)
                response = request.execute()

    def list_files(self, callback_fn):
        request = self.service.files().list()
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
