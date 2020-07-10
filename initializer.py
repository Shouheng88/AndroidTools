#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shutil
import os
import time
import json
import logging
from importer import Importer as Importer
from file_operator import JsonOperator as JsonOperator
from config import REPO_CONFIG_PATH
from config import APP_CONFIG_PATH
from config import APP_LANGUAGE_CONFIG_PATH
from config import REPO_CONFIG_PATH_PREFIX

# 项目初始化工具类
class Initializer:
    # 初始化
    def __init__(self):
        pass

    # 仓库是否已经初始化
    def is_repo_initialized(self):
        return os.path.exists(REPO_CONFIG_PATH)

    # 初始化项目
    def initialize(self, andoird_dir, ios_dir, support_languages):
        logging.debug("[initialize] android dir : " + str(andoird_dir) + " ios dir : " + str(ios_dir) + " support languages : " + str(support_languages))
        # 备份 & 移除配置文件
        if os.path.exists(REPO_CONFIG_PATH):
            dest_path = REPO_CONFIG_PATH_PREFIX % (time.strftime('%Y-%m-%d %M-%I-%S', time.localtime()))
            shutil.copyfile(REPO_CONFIG_PATH, dest_path)
            os.remove(REPO_CONFIG_PATH)
        # 添加支持的多语言
        appConfig.initialize()
        appConfig.add_support_languages(support_languages)
        appConfig.android_resources_root_directory = andoird_dir
        appConfig.ios_resources_root_directory = ios_dir
        # 生成多语言仓库文件
        importer = Importer(appConfig)
        if len(andoird_dir) > 0:
            importer.import_android_resources()
        if len(ios_dir) > 0:
            importer.import_ios_resources()
        # 将配置写入到文件中
        appConfig.write_to_json()
        importer.gen_repo_config()

# 应用配置
class AppConfig:
    # 初始化
    def __init__(self):
        self.language = "" # 当前使用的多语言
        self.support_languages = [] # 支持的语言
        self.languages = {} # 所有多语言
        self.android_resources_root_directory = "" # Android 多语言资源根目录
        self.ios_resources_root_directory = "" # iOS 多语言资源根目录
        self.ios_language_black_list = [] # iOS 多语言黑名单，指语言缩写存在于 Android 而不存在于 iOS 中的
        self.android_language_black_list = [] # Android 多语言黑名单，指语言缩写存在于 iOS 而不存在于 Android 中的
        self.translate_excel_output_directory = "" # 翻译 Excel 导出文件位置
        # 加载配置文件
        with open(APP_CONFIG_PATH, "r") as f:
            config_json = json.load(f)
            self.language = config_json["language"]
            self.support_languages = config_json["support_languages"]
            self.languages = config_json["languages"]
            self.android_resources_root_directory = config_json.get("android_resources_root_directory")
            self.ios_resources_root_directory = config_json.get("ios_resources_root_directory")
            self.ios_language_black_list = config_json.get("ios_language_black_list")
            self.android_language_black_list = config_json.get("android_language_black_list")
            self.translate_excel_output_directory = config_json.get("translate_excel_output_directory")

    # 初始化应用配置
    def initialize(self):
        self.support_languages.clear()

    # 添加多语言支持
    def add_support_languages(self, support_languages):
        for support_language in support_languages:
            # 过滤已经存在的多语言
            if support_language not in self.support_languages:
                self.support_languages.append(support_language)
        logging.debug("Added support languages : " + str(self.support_languages))

    # 将配置写入到 json 文件中
    def write_to_json(self):
        json_obj = {
            "language": self.language,
            "support_languages": self.support_languages,
            "languages": self.languages,
            "ios_language_black_list": self.ios_language_black_list,
            "android_language_black_list": self.android_language_black_list,
            "ios_resources_root_directory": self.ios_resources_root_directory,
            "android_resources_root_directory": self.android_resources_root_directory,
            "translate_excel_output_directory": self.translate_excel_output_directory
        }
        jsonOperator = JsonOperator()
        jsonOperator.write_json(APP_CONFIG_PATH, json_obj)

# 应用多语言工具类，用于翻译工具的多语言
class LanguageFactory:
    # 初始化
    def __init__(self):
        self.entries = {}

    # 加载多语言资源
    def load_languages(self):
        jsonOperator = JsonOperator()
        self.entries = jsonOperator.read_json(APP_LANGUAGE_CONFIG_PATH)

    # 获取多语言词条
    def get_entry(self, name):
        return self.entries[name][appConfig.language]

# the singleton app config bean
appConfig = AppConfig()
