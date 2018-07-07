#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import translator
import logging
import os

def run_commond():
    '''用于在命令行窗口中执行的代码块'''
    config_logging()
    show_msg()    
    
    while True:
        msg = input('>>> ')
        cmd = get_commond(msg)

        if cmd == 'exit':
            break
        if cmd == 'help':
            on_help()
        elif cmd == 'translate':
            on_translate(msg)
        elif cmd == 'generate':
            on_generate(msg)
        elif cmd == 'status':
            on_status(msg)
        else:
            print('Invalid commond')        
    print('程序已退出')
    input()

def show_msg():
    '''输出程序的提示信息'''
    print('\n欢迎使用 Android 字符串翻译小工具\n\n'
        + '用法示例：\n'
        + '    1. 获取帮助请使用命令：\'help\'\n'
        + '    2. 根据当前路径下的 strings.xml 生成用于翻译的 Excel，并且指定翻译的语言: \n' 
        + '       translate zh-rCN,zh-rTW,jp,fr\n' 
        + '    3. 根据当前路径下的 Translate.xls 生成各种需要翻译的 strings.xml：generate\n'
        + '    4. 检查翻译进度：status\n'
        + '    5. 结束程序使用命令：\'exit\'\n\n'
        + '项目地址：https://github.com/Shouheng88/Android-translator\n'
        + '作者：WngShhng\n')

def on_help():
    '''输入帮助'''
    show_msg()

def config_logging():
    '''配置日志'''
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    logging.basicConfig(filename='translator.log', filemode='a', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

def get_commond(msg):
    '''获取输入的命令'''
    msg = msg.strip()
    logging.debug('inputed mssage ' + msg)
    arr = msg.split(' ')
    if len(arr) == 0:
        logging.debug('no commond')
        return 'invalid commond'
    return arr[0].strip()

def get_params(cmd, msg):
    '''获取输入的命令的参数'''
    msg = msg.strip()
    logging.debug(msg)
    
    index = msg.find(cmd)
    if index == -1:
        return []
    
    start = len(cmd)+index
    return msg[start:].strip().split(' ')

def on_translate(msg):
    '''翻译'''
    logging.debug('========== translate ')
    if not check_excel_exists():
        return
    if not check_strings_exists():
        return
    params = get_params('translate', msg)
    logging.debug(params)
    if len(params) == 0:
        print('Invliad params ')
        return
    languages = params[0].split(',')
    translator.create_translate_resources(languages)

def check_excel_exists():
    '''创建翻译的 Excel 之前检验该文件是否已经存在，防止覆盖导致用户数据丢失'''
    if os.path.exists(translator.EXCEL_FILE_NAME):
        msg = input('文件 ' + translator.EXCEL_FILE_NAME + ' 已存在，继续操作将会覆盖之前的文件，是否继续操作？(Y/N)\n')
        cmd = msg.strip().lower()
        if cmd == 'y' or cmd == 'yes':
            return True
        else:
            return False
    return True

def check_strings_exists():
    '''创建翻译的 Excel 之前检验该 strings.xml 是否存在，如果不存在则无法创建Excel'''
    if not os.path.exists(translator.STRINGS_XML_FILE_NAME):
        print('文件 ' + translator.STRINGS_XML_FILE_NAME + ' 不存在，添加该文件到当前目录之后再尝试\n')
        return False
    return True

def on_generate(msg):
    '''根据翻译的结果生成资源'''
    logging.debug('========== generate ')
    if not check_excel_for_generate():
        return
    translator.create_translated_resources()

def check_excel_for_generate():
    '''在生成各国的翻译的字符串资源之前检验 Excel 文件是否存在'''
    if not os.path.exists(translator.EXCEL_FILE_NAME):
        print('文件 ' + translator.EXCEL_FILE_NAME + ' 不存在，添加该文件到当前目录之后再尝试\n')
        return False
    return True

def on_status(msg):
    '''检查当前的翻译状态'''
    logging.debug('========== status')
    if not check_excel_for_generate():
        return
    result = translator.get_translate_status()
    for k,v in result.items():
        print(k + (' : %.2f'%(v)))

run_commond()