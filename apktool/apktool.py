#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
/////////////////////////////////////////........................
//                                       ........................
//         The APK Tool Wrapper          ........................
//                                       ........................
/////////////////////////////////////////........................
'''

import os, sys, shutil, logging
import hashlib
import traceback
from typing import List
sys.path.insert(0, '../')
import global_config

SMALI_MIX_DIRECTORY = "smali_mix"
ERROR_APK_FILE_NOT_EXISTS = "-1"

class DecompileConfiguration:
    def __init__(self) -> None:
        # Should delete and re-decompile if given decompiled files or mixed smali files exists.
        self.force = False

def decompile(apk: str, configuration: DecompileConfiguration) -> str:
    '''Decompile the APK.'''
    if not os.path.exists(apk):
        return ERROR_APK_FILE_NOT_EXISTS
    with open(apk, 'rb') as fp:
        data = fp.read()
    file_md5 = hashlib.md5(data).hexdigest()
    out = "./workspace_%s" % file_md5
    if os.path.exists(out) and not configuration.force:
        return os.path.join(out, SMALI_MIX_DIRECTORY)
    try:
        os.system("sh ../bin/apktool/apktool.sh D %s -o %s" % (apk, out))
    except BaseException as e:
        logging.error('Error while decopiling:\n %s' % traceback.format_exc())
    return out

def mix_all_smalis(dir: str, configuration: DecompileConfiguration) -> str:
    '''
    Mix all smali directories under given dir.
    '''
    mix_to = os.path.join(dir, SMALI_MIX_DIRECTORY)
    if os.path.exists(mix_to) and not configuration.force:
        return mix_to
    files = os.listdir(dir)
    smalis = []
    for f in files:
        if f.startswith("smali") and f != SMALI_MIX_DIRECTORY:
            # search_under_smali(os.path.join(dir, f), configuration)
            smalis.append(os.path.join(dir, f))
    logging.info("Mixing " + str(smalis))
    # Mix all smali files internal.
    return _mix_all_smalis(mix_to, smalis)

def decompile_and_mix_all_smalis(apk: str, configuration: DecompileConfiguration) -> str:
    '''Decompile given apk, mix all smali files together and return the mixed path.'''
    decompile_dir = decompile(apk, configuration)
    if decompile_dir == ERROR_APK_FILE_NOT_EXISTS:
        return ERROR_APK_FILE_NOT_EXISTS
    else:
        return mix_all_smalis(decompile_dir, configuration)

def _mix_all_smalis(mix_to: str, smalis: List[str]) -> str:
    '''
    Mix all smali directories to one to reduce the complexity of the alogrithm.
    Also we can make a more interesting things based on mixed smalis.
    '''
    progress = 1
    for smali in smalis:
        print(" >>> Mixing [%s] %d%%" % (smali, progress*100/len(smalis)), end = '\r')
        logging.info(" >>> Mixing [%s] %d%%" % (smali, progress*100/len(smalis)))
        try:
            shutil.copytree(smali, mix_to, dirs_exist_ok=True)
        except shutil.Error as e:
            for src, dst, msg in e.args[0]:
                print(dst, src, msg)
        progress = progress + 1
    return mix_to

if __name__ == "__main__":
    '''Program entrance.'''
    global_config.config_logging('../log/app.log')
    configuration = DecompileConfiguration()
    dir = decompile_and_mix_all_smalis("/Users/wangshouheng/Desktop/apkanalyse/app_.apk", configuration)
    print(dir)
