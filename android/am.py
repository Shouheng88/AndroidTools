#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ////////////////////////////////////////////////////////////////////
# 
# The Android Debug Bridge Wrapper Project by Python
# 
# @Author Mr.Shouheng
# 
# @References:
# - https://developer.android.com/studio/command-line/adb?hl=zh-cn#am
# 
# ////////////////////////////////////////////////////////////////////

import logging
from time import sleep
from typing import List
from adb import *
import sys
sys.path.insert(0, '../')
import global_config

class ProcessInfo:
    '''Process information wrapper object.'''
    def __init__(self, pro: str, pid: str):
        self.pro = pro
        self.pid = pid

    def __str__(self) -> str:
        return "%s(%s)" % (self.pro, self.pid)

def stop_app_by_package_name(pkg: str, serial: str = None) -> bool:
    '''Stop App of given package name.'''
    return os_system("adb %s shell am force-stop %s ", serial, pkg) == 0

def get_launcher_of_package_name(pkg: str, serial: str = None) -> str:
    '''Get launcher class of given package name.'''
    out = os_popen("adb %s shell dumpsys package %s ", serial, pkg)
    index = out.find('Category: "android.intent.category.LAUNCHER"')
    part = out[0:index]
    s_index = part.rfind(pkg)
    part = part[s_index:index]
    e_index = part.find(' ')
    launcher = part[0:e_index]
    return launcher

def start_app_by_package_name(pkg: str, serial: str = None) -> bool:
    '''Start App by launcher class.'''
    launcher = get_launcher_of_package_name(pkg, serial)
    return os_system("adb %s shell am start %s ", serial, launcher) == 0

def restart_app_by_package_with_profiling(pkg: str, file: str, serial: str = None) -> int:
    '''Restart APP with given package name.'''
    stop_app_by_package_name(pkg, serial)
    launcher = get_launcher_of_package_name(pkg, serial)
    ret = os_popen("adb %s shell am start -n %s --start-profiler %s --sampling %s ", serial, launcher, file, '10')
    logging.debug("Start info: " + ret)
    return 1

def stop_profiler_and_download_trace_file(pkg: str, file: str, to: str, serial: str = None) -> int:
    '''Stop profiler and download the trace file to local.'''
    pros = get_processes_of_pcakage_name(pkg, serial)
    logging.debug("Try to kill process : " + str(pros[0]))
    out = os_popen("adb %s shell am profile stop %s ", serial, pros[0].pid)
    logging.debug("Stop profiler: " + out)
    sleep(10) # Delays for few seconds, currently may writing to the profiler file. (It's emprt now.)
    ret = pull(file, to, serial)
    logging.debug("Pull file from %s to %s : %s" % (file, to, str(ret)))
    return ret

def restart_app_by_with_profiling_and_duration(pkg: str, to: str, duration: int, serial: str = None) -> int:
    '''
    Restart APP and profiler by package name.
    - pkg:      package name
    - to:       local file path to store the profiler file
    - duration: the time duration to collect the profiler data
    '''
    smapling_file = "/data/local/tmp/temp_sampling.trace"
    restart_app_by_package_with_profiling(pkg, smapling_file, serial)
    sleep(duration)
    return stop_profiler_and_download_trace_file(pkg, smapling_file, to, serial)

def dumpheap_by_package(pkg: str, to: str, serial: str = None) -> int:
    '''Dumpheap of given package.'''
    pros = get_processes_of_pcakage_name(pkg, serial)
    temp = "/data/local/tmp/temp.heap"
    if len(pros) == 0:
        return -1
    logging.debug("Try to dump process : " + str(pros[0]))
    os_system("adb %s shell am dumpheap %s %s ", serial, pros[0].pid, temp)
    return pull(temp, to, serial) 

def dumpheap_by_package(pkg: str, process_name: str, to: str, serial: str = None) -> int:
    '''Dumpheap of given package.'''
    pros = get_processes_of_pcakage_name(pkg, serial)
    temp = "/data/local/tmp/temp.heap"
    if len(pros) == 0:
        return -1
    pro = pros[0]
    for p in pros:
        if p == process_name:
            pro = p
    logging.debug("Try to dump process : " + str(pro))
    os_system("adb %s shell am dumpheap %s %s ", serial, pro.pid, temp)   
    return pull(temp, to, serial)

def restart_app_by_package_name(pkg: str, serial: str = None) -> bool:
    '''Restart App by package name.'''
    stop_app_by_package_name(pkg, serial)
    return start_app_by_package_name(pkg, serial)

def get_processes_of_pcakage_name(pkg: str, serial: str = None) -> List[ProcessInfo]:
    '''Get all processes info of package name.'''
    processes = []
    # The 'awk' command is invlaid on adb shell, so it will take into effect.
    text = os_popen("adb %s shell \"ps -ef|grep %s|grep -v grep| awk \'{print $1}\'\"", serial, pkg)
    lines = [line.strip() for line in text.split('\n')]
    for line in lines:
        parts = [col.strip() for col in line.split(' ')]
        cols = []
        for part in parts:
            if part != '':
                cols.append(part)
        if len(cols) == 0:
            continue
        pid = cols[1]
        pro = cols[7].removeprefix(pkg)
        if pro == '':
            pro = ':main'
        process = ProcessInfo(pro, pid)
        processes.append(process)
    return processes

def get_top_activity_info(serial: str = None) -> str:
    '''Get top activities info.'''
    return os_popen("adb %s shell dumpsys activity top", serial)

def capture_screen(to: str, serial: str = None) -> int:
    '''Capture screen.'''
    temp = "/sdcard/screen.png"
    os_system("adb %s shell screencap %s ", serial, temp)
    return pull(temp, to, serial)

if __name__ == "__main__":
    global_config.config_logging('../log/app.log')
    TEST_PACKAGE_NAME = ""
    TEST_DEVICE_SERIAL = "emulator-5556"
    TEST_APK_PATH = "/Users/wangshouheng/downloads/Snapdrop-0.3.apk"
    TEST_LOCAL_FILE = "adb.py"
    TEST_REMOTE_DIR = "/sdcard"
    TEST_REMOTE_FILE = "/sdcard/adb.py"
    # stop_app_by_package_name(TEST_PACKAGE_NAME)
    # stop_app_by_package_name(TEST_PACKAGE_NAME, TEST_DEVICE_SERIAL)
    # print(get_launcher_of_package_name(TEST_PACKAGE_NAME))
    # print(get_launcher_of_package_name(TEST_PACKAGE_NAME, TEST_DEVICE_SERIAL))
    # print(start_app_by_package_name(TEST_PACKAGE_NAME))
    # print(start_app_by_package_name(TEST_PACKAGE_NAME, TEST_DEVICE_SERIAL))
    # print_list(get_processes_of_pcakage_name(TEST_PACKAGE_NAME))
    # print_list(get_processes_of_pcakage_name(TEST_PACKAGE_NAME, TEST_DEVICE_SERIAL))
    # print(get_top_activity_info())
    # print(get_top_activity_info(TEST_DEVICE_SERIAL))
    # os_system("adb %s shell am > ./am.md", TEST_DEVICE_SERIAL)
    # restart_app_by_with_profiling_and_duration(TEST_PACKAGE_NAME, "~/desktop/sampling.trace", 6, TEST_DEVICE_SERIAL)
    # dumpheap_by_package(TEST_PACKAGE_NAME, ":main", "~/desktop/file.heap", TEST_DEVICE_SERIAL)
    # capture_screen("~/desktop/screen.png")
