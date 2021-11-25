#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
////////////////////////////////////////////////////////////////////
//               Android language files merge tool
// Usage: 
//    python merge.py 
//        -f the_path_of_langauge_file_to_merge_from 
//        -t the_path_of_language_file_to_merge_to
// @Author: Mr.Shouheng 
////////////////////////////////////////////////////////////////////
'''

import sys, getopt
import logging
import sys
sys.path.insert(0, '../')
import global_config
from files.xmlfiles import read_android_strings, write_android_resources

command_info = "\
Options: \n\
    -h[--help]               Help info\n\
    -f[--from]               Languages file to merge from\n\
    -t[--to]                 Languages file to merge to\
"

def __show_invalid_command(info: str):
    '''Show invliad command info.'''
    print('Error: Unrecognized command: %s' % info)
    print(command_info)     

class MergeInfo:
    ''''Merge info object.'''
    def __init__(self, merge_from: str, merge_to: str):
        self.merge_from = merge_from
        self.merge_to = merge_to

def __parse_command(argv) -> MergeInfo:
    '''Parse merge info from input command.'''
    try:
        # : and = means accept arguments
        opts, args = getopt.getopt(argv, "-h:-f:-t:", ["help", "from=", 'to='])
    except BaseException as e:
        __show_invalid_command(str(e))
        sys.exit(2)
    if len(opts) == 0:
        __show_invalid_command('empty parameters')
        return
    merge_from = merge_to = None
    for opt, arg in opts:
        if opt in ('-f', '--from'):
            merge_from = arg
        elif opt in ('-t', '--to'):
            merge_to = arg
        elif opt in ('-h', '--help'):
            print(command_info)
            return
    if merge_from == None or merge_to == None:
        __show_invalid_command('Launchage merge file required')
        return
    return MergeInfo(merge_from, merge_to)

def __do_merge(info: MergeInfo):
    ''''Merge launguage files.'''
    strings_from = read_android_strings(info.merge_from)
    strings_to = read_android_strings(info.merge_to)
    for k, v in strings_from.items():
        strings_to[k] = v
    write_android_resources(strings_to, info.merge_to)

def __execute(argv):
    ''''Execute command.'''
    # Parse command.
    info = __parse_command(argv)
    if info == None:
        return
    logging.debug(">> Merging launguages from [" + str(info.merge_from) + "] to [" + str(info.merge_to)+ "].")
    __do_merge(info)

if __name__ == "__main__":
    '''Program entrance.'''
    global_config.config_logging('../log/app.log')
    __execute(sys.argv[1:])
