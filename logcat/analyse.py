#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
////////////////////////////////////////////////////////////////////
//                Android logcat analyse tool
// Usage:
//    python analyse.py 
//        -f the_logcat_file_to_analyse
// References:
//    - Description about logcat: 
//      https://developer.android.com/studio/debug/am-logcat 
// @Author: Mr.Shouheng 
////////////////////////////////////////////////////////////////////
"""

import sys, getopt
import logging
import sys
import re
import time
from datetime import datetime
from typing import List
sys.path.insert(0, '../')
import global_config

LOGCAT_LINE_PATTERN = "^\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}\.\d{1,3}"

command_info = "\
Options: \n\
    -h[--help]               Help info\n\
    -f[--file]               Log file to analyse\n\
    -p[--package]            Package name of analysing log\
"

def __show_invalid_command(info: str):
    '''Show invliad command info.'''
    print('Error: Unrecognized command: %s' % info)
    print(command_info)    

class AnalyseInfo:
    ''''Analyse info object.'''
    def __init__(self, package: str, path: str):
        self.package = package
        self.path = path

class AnalyseLineInfo:
    '''Line info.'''
    def __init__(self, time: int, pid: str, tid: str, level: str, tag: str) -> None:
        self.time = time
        self.pid = pid
        self.tid = tid
        self.level = level
        self.tag = tag

def __parse_command(argv) -> AnalyseInfo:
    '''Parse analyse info from input command.'''
    try:
        # : and = means accept arguments
        opts, args = getopt.getopt(argv, "-h:-p:-f:", ["help", "package=", 'file='])
    except BaseException as e:
        __show_invalid_command(str(e))
        sys.exit(2)
    if len(opts) == 0:
        __show_invalid_command('empty parameters')
        return
    package = path = None
    for opt, arg in opts:
        if opt in ('-f', '--file'):
            path = arg
        elif opt in ('-p', '--package'):
            package = arg
        elif opt in ('-h', '--help'):
            print(command_info)
            return
    if package == None or path == None:
        __show_invalid_command('Package or log output path required!')
        return
    return AnalyseInfo(package, path)

def __execute(argv):
    ''''Execute command.'''
    # Parse command.
    info = __parse_command(argv)
    if info == None:
        return
    logging.info(">> Collect logcat for package [" + info.package + "].")
    # Read and analyse logcat file
    __do_anlyse(info)

def __do_anlyse(info: AnalyseInfo):
    '''Do analyse job.'''
    f = open(info.path)
    line = f.readline()
    tag_count = {}
    while line: 
        matched = re.match(LOGCAT_LINE_PATTERN, line)
        if matched is not None:
            line_info = __do_analyse_line(line)
            if line_info.tag not in tag_count:
                tag_count[line_info.tag] = []
            tag_count[line_info.tag].append(line_info)
        line = f.readline() 
    f.close()
    for k, v in sorted(tag_count.items(), key = lambda kv:(len(kv[1]), len(kv[0]))):
        print(k + ": " + str(len(v)))

def __do_analyse_line(line: str) -> AnalyseLineInfo:
    '''Analyse given line.'''
    time_str = re.match(LOGCAT_LINE_PATTERN, line).group(0)
    left = line.removeprefix(time_str).strip()
    index = left.find(' ')
    pid = left[0:index]
    left = left.removeprefix(pid).strip()
    index = left.find(' ')
    tid = left[0:index]
    left = left.removeprefix(tid).strip()
    index = left.find(' ')
    level = left[0:index]
    left = left.removeprefix(level).strip()
    index = left.find(':')
    tag = left[0:index]
    time_array = time.strptime('2021-' + time_str, "%Y-%m-%d %H:%M:%S.%f")
    time_stamp = int(time.mktime(time_array))
    return AnalyseLineInfo(time_stamp, pid, tid, level, tag)

if __name__ == "__main__":
    '''Program entrance.'''
    global_config.config_logging('../log/app.log')
    __execute(sys.argv[1:])
