#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import *
import logging
import os
import threading
from tkinter.filedialog import askdirectory
from tkinter.messagebox import askokcancel
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo
from tkinter.messagebox import showwarning
from initializer import appConfig as appConfig
from repository import repository as repository
from initializer import Initializer
from importer import Importer as Importer
from generator import Generator as Generator
from translator import Translator as Translator

# 仓库初始化对话框
class RepoInitDialog(Frame):
    # 初始化
    def __init__(self, root):
        self.root = root
        self.android_resources_dir = StringVar()
        self.ios_resources_dir = StringVar()
        self.support_languages = {}
        Frame.__init__(self, root)
        # 多语言资源根目录选择
        fileFrame = Frame(root)
        fileFrame.pack()
        Label(fileFrame, text=">> 初始化：项目多语言仓库初始化", justify=CENTER).grid(row=1, column=1)
        Label(fileFrame, text="1. 选择 Android 多语言资源根目录:", justify=LEFT).grid(row=2, column=1)
        Entry(fileFrame, textvariable=self.android_resources_dir).grid(row=2, column=2)
        Button(fileFrame, text="选择", command=self.select_android_directory).grid(row=2, column=3)
        Label(fileFrame, text="2. 选择 iOS 多语言资源根目录:", justify=LEFT).grid(row=3, column=1)
        Entry(fileFrame, textvariable=self.ios_resources_dir).grid(row=3, column=2)
        Button(fileFrame, text="选择", command=self.select_ios_directory).grid(row=3, column=3)
        # 选择要支持的语言
        languageFrame = Frame(root)
        languageFrame.pack()
        languages = appConfig.languages
        colCount = -1
        for k,v in languages.items():
            colCount = colCount + 1
            self.support_languages[v] = BooleanVar()
            Checkbutton(languageFrame, text=k, variable=self.support_languages[v]).grid(row=2, column=colCount)
        # 初始化按钮
        startFrame = Frame(root)
        startFrame.pack()
        Button(startFrame, text="初始化", command=self.initialize_repo).grid(row=1, column=1)

    # 选择 Android 多语言资源根目录
    def select_android_directory(self):
        self.android_resources_dir.set(askdirectory())
        logging.debug(self.android_resources_dir)

    # 选择 iOS 多语言资源根目录
    def select_ios_directory(self):
        self.ios_resources_dir.set(askdirectory())
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
        init.initialize(self.android_resources_dir.get(), self.ios_resources_dir.get(), support_languages)
        # 初始化完毕
        result = askokcancel(title = '初始化完成', message='已完成项目仓库初始化，请重启程序')
        if result:
            self.root.quit()

# 主程序页面
class MainDialog(Frame):
    # 初始化
    def __init__(self, root):
        self.importer = Importer(appConfig)
        self.generator = Generator(appConfig)
        self.translate_progress = StringVar()
        self.translate_started = False
        Frame.__init__(self, root)
        frame = Frame(root)
        frame.pack()
        # 更新词条
        # Label(frame, text="", justify=LEFT).grid(row=1, column=1)
        Label(frame, text="1、更新多语言词条：", justify=LEFT).grid(row=2, column=1)
        Button(frame, text="更新 Android 多语言词条", command=self.update_android_resource).grid(row=2, column=2)
        Button(frame, text="更新 iOS 多语言词条", command=self.update_ios_resource).grid(row=2, column=3)
        # 自助翻译
        # Label(frame, text="", justify=LEFT).grid(row=3, column=1)
        Label(frame, text="2、自助翻译：", justify=LEFT).grid(row=4, column=1)
        Button(frame, text="开始翻译", command=self.auto_translate).grid(row=4, column=2)
        Label(frame, textvariable=self.translate_progress).grid(row=4, column=3)
        # 导入翻译资源 导出翻译资源
        # Label(frame, text="", justify=LEFT).grid(row=5, column=1)
        Label(frame, text="3、导出/导入翻译资源(Excel)：", justify=LEFT).grid(row=6, column=1)
        Button(frame, text="导出翻译资源(Excel)", command=self.generate_translate_resources).grid(row=6, column=2)
        Button(frame, text="导入翻译资源(Excel)", command=self.import_translated_excel).grid(row=6, column=3)
        # 生成多语言资源
        # Label(frame, text="", justify=LEFT).grid(row=7, column=1)
        Label(frame, text="4、生成多语言资源：", justify=LEFT).grid(row=8, column=1)
        Button(frame, text="生成 Android 多语言资源", command=self.generate_android_resources).grid(row=8, column=2)
        Button(frame, text="生成 iOS 多语言资源", command=self.generate_ios_resources).grid(row=8, column=3)

    # 生成 Android 多语言资源
    def generate_android_resources(self):
        # 判断没有翻译的词条数量
        ret = repository.get_repo_state()
        missed_cuount = ret["missed_count"]
        if missed_cuount != 0:
            result = askokcancel(title="警告", message="存在 %d 个词条没有完全翻译！仍然生成？" % missed_cuount)
            if result:
                self.__generate_android_resources_finaly()
        else:
            self.__generate_android_resources_finaly()

    # 生成 iOS 多语言资源
    def generate_ios_resources(self):
        # 判断没有翻译的词条数量
        ret = repository.get_repo_state()
        missed_cuount = ret["missed_count"]
        if missed_cuount != 0:
            result = askokcancel(title="警告", message="存在 %d 个词条没有完全翻译！仍然生成？" % missed_cuount)
            if result:
                self.__generate_ios_resources_finaly()
        else:
            self.__generate_ios_resources_finaly()

    # 生成用来翻译的 Excel 表格
    def generate_translate_resources(self):
        # 导出到的文件夹
        if len(appConfig.translate_excel_output_directory) == 0:
            appConfig.translate_excel_output_directory = askdirectory()
            appConfig.write_to_json()
        # 导出 Excel 文件
        self.generator.gen_translate_excel(appConfig.translate_excel_output_directory)
        showinfo(title='导出完成', message='已导出翻译 Excel 到 %s ！' % appConfig.translate_excel_output_directory)

    # 导入翻译资源
    def import_translated_excel(self):
        f = askopenfilename(title='选择 Excel 文件', filetypes=[('Excel', '*.xlsx'), ('All Files', '*')])
        self.importer.import_translated_excel(f)
        showinfo(title='更新完成', message='已更新到多语言仓库！')

    # 更新 Android 多语言
    def update_android_resource(self):
        self.importer.update_android_resource()
        showinfo(title='更新完成', message='已更新到多语言仓库！')

    # 更新 iOS 多语言
    def update_ios_resource(self):
        self.importer.update_ios_resource()
        showinfo(title='更新完成', message='已更新到多语言仓库！')

    # 自动进行多语言翻译
    def auto_translate(self):
        ret = repository.get_repo_state()
        missed_cuount = ret["missed_count"]
        if self.translate_started:
            showinfo(title='翻译已启动', message='翻译已经启动，程序正在翻译中……')
            return
        if missed_cuount == 0:
            showinfo(title='已全部翻译完成', message='所有词条已经翻译完毕，无需进行自动翻译')
        else:
            thread = threading.Thread(target=self.__start_translate)
            thread.start()
            self.translate_started = True

    # 正在开始执行翻译
    def __start_translate(self):
        translator = Translator()
        translator.start_translate(self.on_translation_progress_changed, self.on_translation_finished)

    # 通知翻译进度变化
    def on_translation_progress_changed(self, progress):
        logging.debug("On translation progress changed " + str(progress))
        self.translate_progress.set("当前进度: %d%%" % progress)

    # 增加一个完成的回调
    def on_translation_finished(self):
        self.translate_started = False

    # 生成 iOS 资源目录
    def __generate_ios_resources_finaly(self):
        # 如果没设置 iOS 资源目录，则需要选择下
        if len(appConfig.ios_resources_root_directory) == 0:
            appConfig.ios_resources_root_directory = askdirectory()
            appConfig.write_to_json()
        # 生成
        self.generator.gen_ios_resources()

    # 生成 Android 资源目录
    def __generate_android_resources_finaly(self):
        # 如果没设置 Android 资源目录，则需要选择下
        if len(appConfig.android_resources_root_directory) == 0:
            appConfig.android_resources_root_directory = askdirectory()
            appConfig.write_to_json()
        # 生成
        self.generator.gen_android_resources()
