#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os


def preprocessMSTrace(tracefile, filtertype):

    if (len(tracefile.split('/')) > 1):
        out = open("out/" + tracefile.split('/')
                   [-1] + "-preprocess.trace", 'w')
    else:
        out = open("out/" + tracefile + "-preprocess.trace", 'w')
    # else: do nothing

    type_filter = -1
    if filtertype == "write":
        type_filter = 0
    elif filtertype == "read":
        type_filter = 1

    with open("in/" + tracefile) as f:
        # skip header
        for line in f:
            if line[:9] == "EndHeader":
                break

        first_line = True
        offset = 0
        for line in f:
            tok = list(map(str.lstrip, line.split(",")))
            flags = -1

            if tok[0] == "DiskWrite":
                flags = 0
            elif tok[0] == "DiskRead":
                flags = 1

            if flags == -1:
                continue
            if type_filter != -1 and type_filter == flags:
                continue

            if first_line:
                offset = -float(tok[1]) / 1000.0
                first_line = False

            t = {
                "time": (float(tok[1]) / 1000.0) + offset,
                "devno": int(tok[8]),
                "blkno": int(tok[5], 16) / 512,
                "bcount": int(tok[6], 16) / 512,
                "flags": flags,
            }

            out.write("%s %d %d %d %d\n" % ("{0:.3f}".format(
                t['time']), t['devno'], t['blkno'], t['bcount'], t['flags']))

    out.close()


def preprocessBReplayTrace(tracefile, filtertype):

    if (len(tracefile.split('/')) > 1):
        out = open("out/" + tracefile.split('/')
                   [-1] + "-preprocess.trace", 'w')
    else:
        out = open("out/" + tracefile + "-preprocess.trace", 'w')

    type_filter = -1
    if filtertype == "write":
        type_filter = 0
    elif filtertype == "read":
        type_filter = 1

    with open("in/" + tracefile) as f:
        # skip header
        for line in f:
            if line[:5] == "start":
                break

        first_line = True
        for line in f:
            tok = list(map(str.strip, line.split(";")))
            flags = -1

            if tok[3] == "W":
                flags = 0
            elif tok[3] == "R":
                flags = 1

            if flags == -1:
                continue
            if type_filter != -1 and type_filter == flags:
                continue

            if first_line:
                offset = -float(tok[1]) / 1000.0
                first_line = False

            t = {
                "time": (float(tok[0]) * 1000.0),
                "devno": 0,
                "blkno": int(tok[1]),
                "bcount": int(tok[2]),
                "flags": flags,
            }

            out.write("%s %d %d %d %d\n" % ("{0:.3f}".format(
                t['time']), t['devno'], t['blkno'], t['bcount'], t['flags']))

    out.close()


def preprocessUnixBlkTrace(tracefile, filtertype):

    if (len(tracefile.split('/')) > 1):
        out = open("out/" + tracefile.split('/')
                   [-1] + "-preprocess.trace", 'w')
    else:
        out = open("out/" + tracefile + "-preprocess.trace", 'w')

    type_filter = -1
    if filtertype == "write":
        type_filter = 0
    elif filtertype == "read":
        type_filter = 1

    with open("in/" + tracefile) as f:
        # skip header

        for line in f:
            tok = list(map(str.strip, line.split()))
            flags = -1

            if len(tok) > 6 and tok[5] == "D":
                if "W" in tok[6]:
                    flags = 0
                elif "R" in tok[6]:
                    flags = 1

                if flags == -1:
                    continue
                if type_filter != -1 and type_filter == flags:
                    continue

                t = {
                    "time": (float(tok[3]) * 1000.0),
                    "devno": 0,
                    "blkno": int(tok[7]),
                    "bcount": int(tok[9]),
                    "flags": flags,
                }

                out.write("%s %d %d %d %d\n" % ("{0:.3f}".format(
                    t['time']), t['devno'], t['blkno'], t['bcount'], t['flags']))

    out.close()


def preprocessUnixBlkTraceCombine(tracefile, filtertype):

    if (len(tracefile.split('/')) > 1):
        out = open("out/" + tracefile.split('/')
                   [-1] + "-preprocess.trace", 'w')
    else:
        out = open("out/" + tracefile + "-preprocess.trace", 'w')

    type_filter = -1
    if filtertype == "write":
        type_filter = 0
    elif filtertype == "read":
        type_filter = 1

    with open("in/" + tracefile) as f:
        # skip header

        tmpline = []
        for line in f:
            tok = list(map(str.strip, line.split()))
            flags = -1

            if len(tok) > 6 and tok[5] == "Q":
                if "W" in tok[6]:
                    flags = 0
                elif "R" in tok[6]:
                    flags = 1

                if flags == -1:
                    continue
                if type_filter != -1 and type_filter == flags:
                    continue

                try:
                    t = {
                        "time": (float(tok[3]) * 1000.0),
                        "devno": 0,
                        "blkno": int(tok[7]),
                        "bcount": int(tok[9]),
                        "flags": flags,
                    }
                except ValueError:
                    print("ValueError: ", line)
                    continue

                if not tmpline:  # firstline
                    # add a bcount column as memory
                    tmpline = ["{0:.3f}".format(
                        t['time']), t['devno'], t['blkno'], t['bcount'], t['flags'], t['bcount']]
                elif tmpline[2] == (t['blkno'] - tmpline[3]) and tmpline[5] == t['bcount']:
                    tmpline[3] += t['bcount']
                else:
                    out.write("%s %d %d %d %d\n" % (
                        tmpline[0], tmpline[1], tmpline[2], tmpline[3], tmpline[4]))
                    tmpline = ["{0:.3f}".format(
                        t['time']), t['devno'], t['blkno'], t['bcount'], t['flags'], t['bcount']]

        out.write("%s %d %d %d %d\n" %
                  (tmpline[0], tmpline[1], tmpline[2], tmpline[3], tmpline[4]))

    out.close()

# trace format is :
#    0        1        2     3    4     5
# Timestamp,Response,IOType,LUN,Offset,Size


def preprocessSystor17(tracefile, filtertype):
    if (len(tracefile.split('/')) > 1):
        out = open("out/" + tracefile.split('/')
                   [-1] + "-preprocess.trace", 'w')
    else:
        out = open("out/" + tracefile + "-preprocess.trace", 'w')

    type_filter = -1
    if filtertype == "write":
        type_filter = 0
    elif filtertype == "read":
        type_filter = 1

    sector_size = 512

    with open("in/" + tracefile) as f:
        first_line = True
        offset = 0.0
        last_time = 0.0  # check time order
        for line in f:
            tok = list(map(str.strip, line.split(',')))
            flags = -1

            if tok[2] == "W":
                flags = 0
            elif tok[2] == "R":
                flags = 1

            if flags == -1:
                continue
            if type_filter != -1 and type_filter == flags:
                continue

            if first_line:
                offset = -float(tok[0]) * 1000.0  # original is in second
                first_line = False
            else:
                if float(tok[0]) * 1000.0 + offset < last_time:
                    print("time error: ", line)
                    continue

            last_time = float(tok[0]) * 1000.0 + offset

            t = {
                "time": (float(tok[0]) * 1000.0) + offset,
                "devno": 0,
                "blkno": int(tok[4]) / sector_size,
                "bcount": (int(tok[5]) + sector_size - 1) / sector_size,
                "flags": flags,
            }
            out.write("%s %d %d %d %d\n" % ("{0:.3f}".format(
                t['time']), t['devno'], t['blkno'], t['bcount'], t['flags']))
    out.close()
