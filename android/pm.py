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

from adb import *
from typing import List

class PackageInfo:
    def __init__(self, pkg: str = '', path: str = '', uid: str = '', vcode: str = '') -> None:
        self.pkg = pkg
        self.path = path
        self.uid = uid
        self.vcode = vcode
    
    def __str__(self) -> str:
        return "(%s, %s, %s, %s)" % (self.pkg, self.path, self.uid, self.vcode)

def get_packages(serial: str = None) -> List[PackageInfo]:
    '''Get all packages'''
    out = os_popen("adb %s shell pm list packages -f -U -u --show-versioncode ", serial)
    infos = []
    for line in out.split("\n"):
        info = _parse_package_line(line)
        infos.append(info)
    return infos

def get_package_info(pkg: str, serial: str = None) -> PackageInfo:
    '''Get info of one package.'''
    out = os_popen("adb %s shell pm list packages -f -U -u --show-versioncode | grep %s ", serial, pkg)
    return _parse_package_line(out)

def download_apk_of_package(pkg: str, to: str, serial: str = None) -> int:
    '''Download APK of given package name to given path.'''
    info = get_package_info(pkg, serial)
    if len(info.path) > 0:
        return pull(info.path, to, serial)
    return -1

def _parse_package_line(line: str) -> PackageInfo:
    '''Parse package info from line text.'''
    parts = line.split(" ")
    info = PackageInfo()
    for part in parts:
        if len(part) > 0:
            pairs = part.split(":")
            if len(pairs) >= 2:
                if pairs[0] == "package":
                    index = pairs[1].rindex("=")
                    info.path = pairs[1][0:index]
                    info.pkg = pairs[1][index+1:]
                elif pairs[0] == "versionCode":
                    info.vcode = pairs[1]
                elif pairs[0] == "uid":
                    info.uid = pairs[1]
    return info

if __name__ == "__main__":
    TEST_PACKAGE_NAME = "me.shouheng.leafnote"
    TEST_DEVICE_SERIAL = "emulator-5556"
    TEST_APK_PATH = "/Users/wangshouheng/downloads/Snapdrop-0.3.apk"
    TEST_LOCAL_FILE = "adb.py"
    TEST_REMOTE_DIR = "/sdcard"
    TEST_REMOTE_FILE = "/sdcard/adb.py"
    # print_list(get_packages(TEST_DEVICE_SERIAL))
    # print(get_package_info(TEST_PACKAGE_NAME, TEST_DEVICE_SERIAL))
    print(download_apk_of_package(TEST_PACKAGE_NAME, "~/leafnote.apk", TEST_DEVICE_SERIAL))
    # os_system("adb %s shell pm > ./pm", TEST_DEVICE_SERIAL)
