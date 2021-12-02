#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
/////////////////////////////////////////........................
//                                       ........................
//     The APK Tool Wrapper              ........................
//     @Author Shouheng Wang             ........................
//                                       ........................
/////////////////////////////////////////........................
'''

import os, sys, shutil, logging, time, zipfile
import hashlib
import traceback
from typing import List
sys.path.insert(0, '../')
import global_config

SMALI_MIX_DIRECTORY         = "smali_mix"
DECOMPILE_DEFAULT_WORKSPACE = "../../godseye"
ERROR_APK_FILE_NOT_EXISTS   = "-1"

class DecompileConfiguration:
    def __init__(self) -> None:
        # Should delete and re-decompile if given decompiled files or mixed smali files exists.
        self.force = False
        # Try to avoid output in currnt folder, since there may generating too many files
        # which will make the Git analysing very slow.
        self.workspace = DECOMPILE_DEFAULT_WORKSPACE
        self.apk_md5 = ''
        self.decompile_cost = 0
        self.mix_smalis_cost = 0

    def decompile_cost_time(self) -> int:
        '''The time cost in seconds for decompile.'''
        return int(time.time()) - self.decompile_cost

    def mix_smalis_cost_time(self) -> int:
        '''The time cost in seconds for mixing smali files.'''
        if self.mix_smalis_cost == 0:
            return 0
        return int(time.time()) - self.mix_smalis_cost

def decompile(apk: str, configuration: DecompileConfiguration) -> str:
    '''Decompile the APK.'''
    configuration.decompile_cost = int(time.time())
    if not os.path.exists(apk):
        return ERROR_APK_FILE_NOT_EXISTS
    file_md5 = str(int(time.time()))
    try:
        with open(apk, 'rb') as fp:
            data = fp.read()
        file_md5 = hashlib.md5(data).hexdigest()
        configuration.apk_md5 = file_md5
    except BaseException as e:
        logging.error("Error while reading the APK md5:\n%s" % traceback.format_exc())
    out = "%s/workspace_%s" % (configuration.workspace, file_md5)
    if os.path.exists(out) and not configuration.force:
        return out
    # Decompile dex in APK.
    _decompile(apk, out)

def _decompile(apk: str, out: str):
    '''Decompile internal.'''
    file = zipfile.ZipFile(apk)
    dex_list = []
    for name in file.namelist():
        if name.endswith(".dex"):
            dex_list.append(name)
    logging.debug("Decompiling dex list: %s" % str(dex_list))
    progress = 1
    for dex_name in dex_list:
        try:
            # TODO Will unzip the apk and then decompile the dex make the program fast?
            dex = "%s/%s" % (apk, dex_name)
            print(" >>> Decompiling dex [%s] %d%%" % (dex, progress*100/len(dex_list)), end = '\r')
            os.system("java -jar ../bin/baksmali/baksmali.jar d %s -o %s" % (dex, out))
        except BaseException as e:
            logging.error('Error while decopiling:\n%s' % traceback.format_exc())
        progress = progress + 1

def mix_all_smalis(dir: str, configuration: DecompileConfiguration) -> str:
    '''
    Mix all smali directories under given dir. Perhaps, someday, we could make
    use of this feature to make more interesting tools.
    '''
    configuration.mix_smalis_cost = int(time.time())
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
    dir = decompile("/Users/wangshouheng/Desktop/apkanalyse/app_.apk", configuration)
    print(dir)
    print("Decompile cost: %ds" % configuration.decompile_cost_time())
    print("Mix smalis cost: %ds" % configuration.mix_smalis_cost_time())
    # file = zipfile.ZipFile("/Users/wangshouheng/Desktop/apkanalyse/app_.apk")
    # dex_list = []
    # for name in file.namelist():
    #     if name.endswith(".dex"):
    #         dex_list.append(name)
    # print(dex_list)
