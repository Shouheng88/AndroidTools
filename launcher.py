#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import tkinter
from tkinter import Tk
from initializer import LanguageFactory
from initializer import Initializer
from app_gui import MainDialog
from app_gui import RepoInitDialog

def __config_logging():
    '''配置日志'''
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    logging.basicConfig(filename='app.log', filemode='a', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    logging.FileHandler(filename='app.log', encoding='utf-8')

if __name__ == "__main__":
    __config_logging()
    # 加载多语言资源
    factory = LanguageFactory()
    factory.load_languages()
    # Tk
    root = Tk()
    root.title(factory.get_entry("app_title"))
    # 进行项目初始化
    initializer = Initializer()
    if not initializer.is_repo_initialized() :
        # 进入项目初始化页面
        RepoInitDialog(root).pack()
    else:
        # 进入正常编辑页面
        MainDialog(root).pack()
    root.mainloop()
