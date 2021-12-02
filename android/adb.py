#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import List

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

class DeviceInfo:
    '''Adb attached device info.'''
    def __init__(self) -> None:
        self.infos = []

    def append(self, info: str):
        '''Append one info to infos.'''
        self.infos.append(info)

    def __str__(self) -> str:
        ret = ''
        for info in self.infos:
            ret = ret + info + '\n'
        return ret

def get_devices() -> List[DeviceInfo]:
    '''Get all attached devices.'''
    text = os_popen("adb devices -l", None)
    lines = [line.strip() for line in text.split('\n')]
    devices = []
    for line in lines[1:]:
        parts = [part.strip() for part in line.split(' ')]
        device = DeviceInfo()
        index = 0
        for part in parts:
            if len(part) > 0:
                index = index+1
                if index == 1:
                    device.append("serial:" + part)
                elif index == 2:
                    device.append("state:" + part)
                else:
                    device.append(part)
        devices.append(device)
    return devices

def get_version() -> List[str]:
    '''Get adb version info.'''
    text = os_popen("adb version", None)
    lines = [line.strip() for line in text.split('\n')]
    return lines

def reboot(serial: str = None) -> int:
    '''Reboot device.'''
    return os_system("adb %s reboot ", serial)

def export_bugreport(path: str, serial: str = None) -> int:
    '''Export bugreport, ANR log etc.'''
    return os_system("adb %s bugreport %s", serial, path)

def install(apk: str, serial: str = None) -> int:
    '''
    Install given package:
    - apk: path of APK.
    '''
    return os_system("adb %s install %s ", serial, apk)

def uninstall(pkg: str, keep: bool, serial: str = None) -> bool:
    '''
    Uninstall given package.
    - pkg: package name
    - keep: keep the data and cache directories if true, otherwise false.
    '''
    if keep:
        return os_system("adb %s uninstall -k %s ", serial, pkg) == 0
    else:
        return os_system("adb %s uninstall %s ", serial, pkg) == 0

def push(local: str, remote: str, serial: str = None) -> int:
    '''
    Push local file to remote directory.
    - local: local file path
    - remote: the remote path to push to
    '''
    return os_system("adb %s push %s %s", serial, local, remote)

def pull(remote: str, local: str, serial: str = None) -> int:
    '''
    Pull file from remote phone:
    - remote: remote file path
    - local: local to store file
    '''
    return os_system("adb %s pull %s %s", serial, remote, local)

def os_system(command: str, serial: str, *args) -> int:
    '''Execute command by os.system().'''
    f_args = []
    if serial is None:
        f_args.append(" ")
    else:
        f_args.append(" -s %s " % serial)
    f_args.extend(args)
    if len(f_args) == 1 and f_args[0] == " ":
        return os.system(command)
    return os.system(command % tuple(f_args))

def os_popen(command: str, serial: str, *args) -> str:
    '''Execute command by os.popen().'''
    f_args = []
    if serial is None:
        f_args.append(" ")
    else:
        f_args.append(" -s %s " % serial)
    f_args.extend(args)
    if len(f_args) == 1 and f_args[0] == " ":
        out = os.popen(command)
    else:
        out = os.popen(command % tuple(f_args))
    return out.read().strip()

def print_list(list: List):
    '''Print list.'''
    for item in list:
        print(str(item) + ", ")

if __name__ == "__main__":
    TEST_PACKAGE_NAME = "me.shouheng.leafnote"
    TEST_DEVICE_SERIAL = "emulator-5556"
    TEST_APK_PATH = "/Users/wangshouheng/downloads/Snapdrop-0.3.apk"
    TEST_LOCAL_FILE = "adb.py"
    TEST_REMOTE_DIR = "/sdcard"
    TEST_REMOTE_FILE = "/sdcard/adb.py"
    # print_list(get_devices())
    # print(get_version())
    # print(reboot())
    # print(reboot(TEST_DEVICE_SERIAL))
    # print(export_bugreport('~/bugs'))
    # print(export_bugreport('~/bugs', TEST_DEVICE_SERIAL))
    # print(uninstall(TEST_PACKAGE_NAME, False))
    # print(uninstall(TEST_PACKAGE_NAME, False, TEST_DEVICE_SERIAL))
    # print(install(TEST_APK_PATH))
    # print(install(TEST_APK_PATH, TEST_DEVICE_SERIAL))
    # print(os_system("ls -al " + TEST_APK_PATH, None))
    # print(push(TEST_LOCAL_FILE, TEST_REMOTE_DIR, TEST_DEVICE_SERIAL))
    # print(pull(TEST_REMOTE_FILE, "~", TEST_DEVICE_SERIAL))
    # os_system("a", "b", "c", "d", "e")
    pull("/data/local/tmp/temp_sampling.trace", ".", TEST_DEVICE_SERIAL)
