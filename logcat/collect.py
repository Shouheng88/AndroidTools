#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
////////////////////////////////////////////////////////////////////
//                Android logcat collect tool
// Usage:
//    python collect.py 
//        -f force restart or not
//        -p the_package_to_collect_log
//        -l the_path_to_output_log
// Collect log from Android logcat:
//    
// References:
// - Android logcat usage doc: 
//  https://developer.android.com/studio/command-line/logcat?hl=zh-cn
// @Author: Mr.Shouheng 
////////////////////////////////////////////////////////////////////
"""

import os
import sys, getopt
import logging
import signal
import sys
import threading
from time import sleep
from typing import List
sys.path.insert(0, '../')
import global_config
from android.adb import *
from android.am import *

LOGCAT_COLLECT_MAX_TIME      = 10 # 10 minutes

command_info = "\
Options: \n\
    -h[--help]               Help info\n\
    -f[--forcestop]          Should stop living app\n\
    -p[--package]            Package name of analysing\n\
    -l[--log]                Log file path from logcat\
"

def __show_invalid_command(info: str):
    '''Show invliad command info.'''
    print('Error: Unrecognized command: %s' % info)
    print(command_info)

class CollectInfo:
    ''''Collect info object.'''
    def __init__(self, package: str, path: str, fc: str):
        self.package = package
        self.path = path
        self.fc = fc

def __parse_command(argv) -> CollectInfo:
    '''Parse collect info from input command.'''
    try:
        # : and = means accept arguments
        opts, args = getopt.getopt(argv, "-h:-p:-l:-f", ["help", "package=", 'log=', 'forcestop='])
    except BaseException as e:
        __show_invalid_command(str(e))
        sys.exit(2)
    if len(opts) == 0:
        __show_invalid_command('empty parameters')
        return
    package = path = forcestop = None
    for opt, arg in opts:
        if opt in ('-l', '--log'):
            path = arg
        elif opt in ('-p', '--package'):
            package = arg
        elif opt in ('-f', '--forcestop'):
            forcestop = arg
        elif opt in ('-h', '--help'):
            print(command_info)
            return
    if package == None or path == None:
        __show_invalid_command('Package or log output path required!')
        return
    return CollectInfo(package, path, forcestop)

def __logcat_redirect(pro: str, pid: str, info: CollectInfo):
    '''Do logcat redirect.'''
    # Be sure to add the '-d' option, otherwise the logcat won't write to screen.
    os.system("adb shell logcat --pid=" + pid + " -d > " + info.path + "/" + info.package + "" + pro + ".log")

def __kill_collect_process():
    '''Kill current process to stop all logcat collect threads.'''
    out = os.popen("ps -ef | grep collect.py | grep -v grep | awk '{print $2}'")
    pid = out.read().strip()
    logging.debug(">> Collect trying to kill collect process [" + pid + "].")
    # os.system("kill -9 " + pid)
    os.kill(int(pid), signal.SIGTERM)

def __execute(argv):
    ''''Execute command.'''
    # Parse command.
    info = __parse_command(argv)
    if info == None:
        return
    # Restart App if necessary.
    if info.fc != None:
        restart_app_by_package_name(info.package)
    logging.info(">> Collect logcat for package [" + info.package + "].")
    # Parse all process and their pids
    processes = get_processes_of_pcakage_name(info.package)
    logging.info(">> Collect process: [" + str(processes) + "].")
    threads = [threading.Thread]
    for process in processes:
        logging.info(">> Collect process: [" + process.pro + "].")
        thread = threading.Thread(target=__logcat_redirect, args=(process.pro, process.pid, info))
        thread.name = process.pro + "(" + process.pid + ")"
        threads.append(thread)
    for thread in threads:
        thread.start()
        logging.info(">> Collect for process: [" + thread.name + "] started.")
    timer = threading.Timer(LOGCAT_COLLECT_MAX_TIME, __kill_collect_process)
    timer.start()

if __name__ == "__main__":
    '''Program entrance.'''
    global_config.config_logging('../log/app.log')
    __execute(sys.argv[1:])
