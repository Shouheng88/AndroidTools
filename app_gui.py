#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import *
import logging
from tkinter.filedialog import askdirectory
from tkinter.messagebox import askokcancel
from initializer import AppConfig
from initializer import Initializer

# 仓库初始化对话框
class RepoInitDialog(Frame):
    def __init__(self, root):
        self.root = root
        self.android_resources_dir = ""
        self.ios_resources_dir = ""
        self.support_languages = {}
        self.app_config = AppConfig()
        Frame.__init__(self, root)
        # 多语言资源根目录选择
        fileFrame = Frame(root)
        fileFrame.pack()
        Label(fileFrame, text="1. 选择 Android 多语言资源根目录:", justify=LEFT).grid(row=1, column=1)
        Entry(fileFrame, textvariable=self.android_resources_dir).grid(row=1, column=2)
        Button(fileFrame, text="选择", command=self.select_android_directory).grid(row=1, column=3)
        Label(fileFrame, text="2. 选择 iOS 多语言资源根目录:", justify=LEFT).grid(row=2, column=1)
        Entry(fileFrame, textvariable=self.ios_resources_dir).grid(row=2, column=2)
        Button(fileFrame, text="选择", command=self.select_ios_directory).grid(row=2, column=3)
        # 选择要支持的语言
        languageFrame = Frame(root)
        languageFrame.pack()
        languages = self.app_config.get_all_languages()
        colCount = -1
        for k,v in languages.items():
            colCount = colCount + 1
            self.support_languages[v] = BooleanVar()
            cb = Checkbutton(languageFrame, text=k, variable=self.support_languages[v])
            cb.grid(row=2, column=colCount)
        # 初始化按钮
        startFrame = Frame(root)
        startFrame.pack()
        Button(startFrame, text="初始化", command=self.initialize_repo).grid(row=1, column=1)

    # 选择 Android 多语言资源根目录
    def select_android_directory(self):
        self.android_resources_dir = askdirectory()
        logging.debug(self.android_resources_dir)

    # 选择 iOS 多语言资源根目录
    def select_ios_directory(self):
        self.ios_resources_dir = askdirectory()
        logging.debug(self.ios_resources_dir)

    # 初始化仓库
    def initialize_repo(self):
        # 初始化应用配置
        support_languages = []
        for k,v in self.support_languages.items():
            if v.get():
                support_languages.append(k)
        # 初始化项目仓库
        init = Initializer()
        init.initialize(self.android_resources_dir, self.ios_resources_dir, support_languages)
        # 初始化完毕
        result = askokcancel(title = '初始化完成', message='已完成项目仓库初始化，请重启程序')
        if result:
            self.root.quit()

# 主程序页面
class MainDialog(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
