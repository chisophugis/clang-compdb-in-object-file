#!/usr/bin/python
from __future__ import print_function

import sys

print('[')
for i, line in enumerate(sys.stdin):
    if i != 0:
        print(',')
    print(line)
print(']')

