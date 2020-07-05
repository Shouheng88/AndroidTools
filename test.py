#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from translator import BaiduTranslator as Translator
from initializer import Initializer as Initializer
from importer import Importer as Importer
from initializer import AppConfig as AppConfig
import logging

def config_logging():
    '''配置日志'''
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    logging.basicConfig(filename='log/test.log', filemode='a', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    logging.FileHandler(filename='log/test.log', encoding='utf-8')

if __name__ == "__main__":
    config_logging()
    ts = Translator()
    translated = ts.translate("你好啊", "jp")
    print(translated)

    im = Importer(AppConfig())
    im.import_android_resources("/Users/wangshouheng/Desktop/github/python/app-i18n/Android")
    im.gen_repo_config()