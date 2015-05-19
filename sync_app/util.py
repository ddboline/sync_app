#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

HOMEDIR = os.getenv('HOME')

def run_command(command, do_popen=False, turn_on_commands=True):
    """ wrapper around os.system """
    if not turn_on_commands:
        print(command)
        return command
    elif do_popen:
        return os.popen(command)
    else:
        return os.system(command)

def cleanup_path(orig_path):
    """ cleanup path string using escape character """
    return orig_path.replace(' ', '\ ').replace('(', '\(').replace(')', '\)')\
                    .replace('\'', '\\\'').replace('[', '\[')\
                    .replace(']', '\]').replace('"', '\"').replace("'", "\'")\
                    .replace('&', '\&').replace(',', '\,').replace('!', '\!')\
                    .replace(';', '\;').replace('$', '\$')
