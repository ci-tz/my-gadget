#!/usr/bin/env python

'''
This srcipt is used to zerize the time in the trace file.
Use this script as:

./trace_zerize.py trace_file zerized_line

For example, the original trace file is:
1 hello
2 hi
3 error

After running this script as:

./trace_zerize.py trace_file 0

the output will be:

0.0 hello
1.0 hi
2.0 error

It is useful to edit the trace file is the first timestamp is not 0.

'''

import sys

filename = sys.argv[1]
zerized_line = sys.argv[2]

f = open(filename, "r")
start = -1
for l in f.readlines():
    ws = l.split()
    if start == -1:
        start = float(ws[int(zerized_line)])
    ws[int(zerized_line)] = str((float(ws[int(zerized_line)]) - start))
    print(' '.join(ws)) 
