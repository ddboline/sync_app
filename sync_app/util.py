#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Utility functions """
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from subprocess import call, Popen, PIPE

HOMEDIR = os.getenv('HOME')

class PopenWrapperClass(object):
    """ wrapper around subprocess.Popen """
    def __init__(self, command):
        """ init """
        self.command = command
        self.pop_ = Popen(self.command, shell=True, stdout=PIPE,
                          close_fds=True)

    def __enter__(self):
        """ enter """
        return self.pop_

    def __exit__(self, exc_type, exc_value, traceback):
        """ exit """
        if hasattr(self.pop_, '__exit__'):
            return self.pop_.__exit__(exc_type, exc_value, traceback)
        self.pop_.wait()
        if exc_type or exc_value or traceback:
            return False
        else:
            return True

def run_command(command, do_popen=False, turn_on_commands=True,
                single_line=False):
    """ wrapper around os.system """
    if not turn_on_commands:
        print(command)
        return command
    elif do_popen:
        return PopenWrapperClass(command)
    elif single_line:
        with PopenWrapperClass(command) as pop_:
            return pop_.stdout.read()
    else:
        return call(command, shell=True)

def cleanup_path(orig_path):
    """ cleanup path string using escape character """
    chars_to_escape = ' ()"[]&,!;$' + "'"
    for ch_ in chars_to_escape:
        orig_path = orig_path.replace(ch_, r'\%c' % ch_)
    return orig_path

def walk_wrapper(direc, callback, arg):
    """ wrapper around os.walk for py2/py3 compatibility """
    if hasattr(os.path, 'walk'):
        os.path.walk(direc, callback, arg)
    elif hasattr(os, 'walk'):
        for dirpath, dirnames, filenames in os.walk(direc):
            callback(arg, dirpath, dirnames + filenames)
