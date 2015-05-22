#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    syncing app,
    default:
        sync gdrive
        sync s3
        sync select local directories
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#import os

from sync_app.sync_utils import sync_gdrive, sync_s3, sync_local

if __name__ == '__main__':
#    sync_gdrive(dry_run=False)
#    sync_s3(dry_run=False)
    sync_local(dry_run=True)
