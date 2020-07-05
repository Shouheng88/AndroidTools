#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shutil
import os
import time
import json
import logging
from importer import Importer as Importer
from file_operator import JsonOperator as JsonOperator

APP_CONFIG_PATH = "config/app.json" # 应用配置文件
REPO_CONFIG_PATH = "config/repo_config.json" # 仓库配置文件地址
APP_LANGUAGE_CONFIG_PATH = "config/app_language_config.json" # 应用多语言配置文件

# 项目初始化工具类
class Initializer:
    # 初始化
    def __init__(self):
        self.app_config = AppConfig()

    # 仓库是否已经初始化
    def is_repo_initialized(self):
        return os.path.exists(REPO_CONFIG_PATH)

    # 获取所有可选语言
    def get_all_languages(self):
        return self.app_config.get_all_languages()

    # 初始化项目
    def initialize(self, andoird_dir, ios_dir, support_languages):
        logging.debug("[initialize] android dir : " + andoird_dir + " ios dir : " + ios_dir + " support languages : ")
        logging.debug(support_languages)
        # 备份 & 移除配置文件
        if os.path.exists(REPO_CONFIG_PATH):
            dest_path = "config/repo_config_" + time.strftime('%Y-%m-%d %M-%I-%S', time.localtime()) + ".json"
            shutil.copyfile(REPO_CONFIG_PATH, dest_path)
            os.remove(REPO_CONFIG_PATH)
        # 添加支持的多语言
        self.app_config.init_app_config()
        self.app_config.add_support_languages(support_languages)
        # 将配置写入到文件中
        self.app_config.write_to_json()
        # 生成多语言仓库文件
        importer = Importer(self.app_config)
        if len(andoird_dir) > 0:
            importer.import_android_resources(andoird_dir)
        if len(ios_dir) > 0:
            importer.import_ios_resources(ios_dir)
        importer.gen_repo_config()

# 应用配置
class AppConfig:
    # 初始化
    def __init__(self):
        self.language = "" # 当前使用的多语言
        self.support_languages = [] # 支持的语言
        self.languages = {} # 所有多语言
        # 加载配置文件
        with open(APP_CONFIG_PATH, "r") as f:
            config_json = json.load(f)
            self.language = config_json["language"]
            self.support_languages = config_json["support_languages"]
            self.languages = config_json["languages"]

    # 初始化应用配置
    def init_app_config(self):
        self.support_languages.clear()

    # 添加多语言支持
    def add_support_languages(self, support_languages):
        for support_language in support_languages:
            if support_language not in self.support_languages:
                self.support_languages.append(support_language)
        logging.debug(self.support_languages)

    # 获取所有的支持的多语言
    def get_all_support_languages(self):
        return self.support_languages

    # 获取所有的可选语言
    def get_all_languages(self):
        return self.languages

    # 当前支持的多语言
    def get_language(self):
        return self.language

    # 将配置写入到 json 文件中
    def write_to_json(self):
        json_obj = {
            "language": self.language,
            "support_languages": self.support_languages,
            "languages": self.languages
        }
        jsonOperator = JsonOperator()
        jsonOperator.write_json(APP_CONFIG_PATH, json_obj)

# 应用多语言工具类
class LanguageFactory:
    # 初始化
    def __init__(self):
        self.entries = {}

    # 加载多语言资源
    def load_languages(self):
        jsonOperator = JsonOperator()
        self.entries = jsonOperator.read_json(APP_LANGUAGE_CONFIG_PATH)
        self.app_config = AppConfig()

    # 获取多语言词条
    def get_entry(self, name):
        return self.entries[name][self.app_config.get_language()]