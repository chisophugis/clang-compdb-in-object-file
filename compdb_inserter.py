#!/usr/bin/env python
from __future__ import print_function

# The thought is that eventually clang itself could embed this information.

import json
import hashlib
import os
import shutil
import sys

CXX = 'clang++'

def sketchy_extract_file(l):
    """Extract the C++ file from the compiler commandline.
    It's "sketchy" because it doesn't implement a full option parser. For
    example, it would be fooled by `clang -DFOO=Bar.cpp`"""
    for s in l:
        if s.endswith('.cpp'):
            return s

def turn_into_c_string_literal(s):
    return json.dumps(s) # Kinda sketchy but should work.

def make_unique_identifer_from(s):
    h = hashlib.sha1()
    h.update(s)
    return '__COMPDB_SYMNAME_' + h.hexdigest()

def insert_compdb_magic(new_argv):
    compdb_entry = {
        'directory': os.getcwd(),
        'command': ' '.join(new_argv), # Needs better quoting logic?
        'file': sketchy_extract_file(new_argv)
    }
    compdb_entry_str = json.dumps(compdb_entry)
    c_string = turn_into_c_string_literal(compdb_entry_str)
    new_argv.append('-D__COMPDB_ENTRY=' + c_string)
    symname = make_unique_identifer_from(compdb_entry_str)
    new_argv.append('-D__COMPDB_SYMNAME=' + symname)
    # Need to use absolute path to CompilationDatabaseMagic.h
    new_argv.extend(['-include', 'CompilationDatabaseMagic.h'])

new_argv = [CXX] + sys.argv[1:]
if '-c' in new_argv:
    insert_compdb_magic(new_argv)
os.execvp(CXX, new_argv)
