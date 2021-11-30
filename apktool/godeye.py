#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
/////////////////////////////////////////         .........
//                                             ..   .....   ..
//    The Android Smali File Searcher       ...   ........   ...
//                                         ...   .........    ...
//    @Author Shouheng Wang                 ..............   ...
//                                             ...............
/////////////////////////////////////////         .........
'''

import os, sys, time, shutil, logging
from typing import List
from smali import SmaliSearcherConfiguration
sys.path.insert(0, '../')
import global_config
from files.jsonfiles import read_json

SMALI_SEARCHER_CONFIGURATION_FILE = "config.json"

def read_configuration() -> SmaliSearcherConfiguration:
    '''Read smali searcher configuration.'''
    json_object = read_json(SMALI_SEARCHER_CONFIGURATION_FILE)
    configuration = SmaliSearcherConfiguration()
    configuration.package = json_object["package"]
    configuration.keywords = json_object["keywords"]
    configuration.traceback = json_object["traceback"]
    configuration.traceback_generation = json_object["traceback_generation"]
    return configuration



if __name__ == "__main__":
    '''Program entrance.'''
    global_config.config_logging('../log/app.log')
