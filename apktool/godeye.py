#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
/////////////////////////////////////////       ......       /////////////////////////////////////////
//                                            ...    ...                                            //
//                                           ...  ..  ...                                           //
//    EYES OF GOD PROJECT                    ...  ..  ...         @Author Shouheng Wang             //
//                                           ...  ..  ...                                           //
//                                            ...    ...                                            //
/////////////////////////////////////////       ......       /////////////////////////////////////////
'''

import logging
import os, sys, getopt
sys.path.insert(0, '../')
import global_config
from files.jsonfiles import read_json
from apktools import DecompileConfiguration, decompile
from smali import SmaliSearcherConfiguration, search_smali, TracebackConfiguration

DEFAULT_GOD_EYE_CONFIGURATION_FILE = "config.json"

class GodEyeCommand:
    '''God's eye command'''
    def __init__(self) -> None:
        self.config_path = DEFAULT_GOD_EYE_CONFIGURATION_FILE

class GodEyeConfiguration:
    def __init__(self) -> None:
        self.apk = ''
        self.force = False
        self.package = ''
        # The methods to search for example 'Ljava/lang/StringBuilder;-><init>()V', or keyword to search.
        self.keywords = []
        self.traceback = TracebackConfiguration()
        self.output = "."

    def __str__(self) -> str:
        return "GodEyeConfiguration [%s][%s][%s][%s][%s][%s]" % (str(self.apk), str(self.force), \
            str(self.package), str(self.keywords), str(self.traceback), str(self.output))

command_info = "\
Options: \n\
    -h[--help]               Help info;\n\
    -p[--path]               The path of the config file.\
"

def execute_command(argv):
    '''Execute command.'''
    command = _parse_command(argv)
    if command is None:
        return
    configuration = _read_god_eye_configuration(command)
    if not _check_god_eye_configuration(configuration):
        msg = "Invliad god eye configuration!"
        print(msg)
        logging.error(msg)
        return
    logging.info("Start to decompile APK [%s]." % configuration.apk)
    smali_path = _decompile_and_return_search_dir(configuration)
    logging.info("Start to search under smali path: %s" % smali_path)
    _search_under_smali_path(smali_path, configuration)

def _read_god_eye_configuration(command: GodEyeCommand) -> GodEyeConfiguration:
    '''Read the god eye configuration.'''
    configuration = GodEyeConfiguration()
    if os.path.exists(command.config_path):
        configuration = _read_configuration(command.config_path)
    logging.info("Read god eye configuration: %s" % str(configuration))
    return configuration

def _check_god_eye_configuration(configuration: GodEyeConfiguration) -> bool:
    '''Check the god eye configuration.'''
    if configuration.apk is None or len(configuration.apk) == 0:
        msg = "Failed: the APK path is required!"
        print(msg)
        logging.error(msg)
        return False
    elif not os.path.exists(configuration.apk):
        msg = "Failed: the specified APK path is not exists!"
        print(msg)
        logging.error(msg)
        return False
    elif not os.path.isfile(configuration.apk):
        msg = "Failed: the specified path is not a valid APK!"
        print(msg)
        logging.error(msg)
        return False
    return True

def _search_under_smali_path(dir: str, configuration: GodEyeConfiguration):
    '''Search under given smali directory.'''
    searcher_configuration = SmaliSearcherConfiguration()
    searcher_configuration.package = configuration.package
    searcher_configuration.keywords = configuration.keywords
    searcher_configuration.traceback = configuration.traceback
    searcher_configuration.output = configuration.output
    search_smali(dir, searcher_configuration)

def _decompile_and_return_search_dir(configuration: GodEyeConfiguration) -> str:
    '''Do decompile to APK and return the directory of smalis to search.'''
    decompile_configuration = DecompileConfiguration()
    decompile_configuration.force = configuration.force
    # If you want to merge all smali files to one and then search under it, use the line below.
    # return decompile_and_mix_all_smalis(command.apk_path, decompile_configuration)
    return decompile(configuration.apk, decompile_configuration)

def _show_invalid_command(info: str):
    '''Show invliad command info.'''
    print('Error! Unrecognized command: %s' % info)
    print(command_info)   

def _read_configuration(path: str) -> GodEyeConfiguration:
    '''Read smali searcher configuration.'''
    json_object = read_json(path)
    configuration = GodEyeConfiguration()
    configuration.apk = json_object["apk"]
    configuration.force = json_object["force"]
    configuration.package = json_object["package"]
    configuration.keywords = json_object["keywords"]
    configuration.output = json_object["output"]
    json_traceback = json_object["traceback"]
    if json_traceback is not None:
        traceback = TracebackConfiguration()
        traceback.enable = json_traceback["enable"]
        traceback.generation = json_traceback["generation"]
        configuration.traceback = traceback
    return configuration

def _parse_command(argv) -> GodEyeCommand:
    '''Parse god eye command from input.'''
    try:
        # : and = means accept arguments
        opts, args = getopt.getopt(argv, "-h:-p:", ["help", 'path='])
    except BaseException as e:
        _show_invalid_command(str(e))
        sys.exit(2)
    command = GodEyeCommand()
    config_path = None
    for opt, arg in opts:
        if opt in ('-p', '--path'):
            config_path = arg
        elif opt in ('-h', '--help'):
            print(command_info)
            return
    if config_path is None:
        msg = "No config file specified, the default config file [%s] will be used" % DEFAULT_GOD_EYE_CONFIGURATION_FILE
        logging.info(msg)
        print(msg)
    return command

if __name__ == "__main__":
    '''
    Program entrance. Usage, for example:
    >> python godeye.py -p config.json
    '''
    global_config.config_logging('../log/app.log')
    execute_command(sys.argv[1:])
