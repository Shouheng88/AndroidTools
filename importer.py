#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import json
from file_operator import XmlOperator as XmlOperator
from file_operator import JsonOperator as JsonOperator

REPO_CONFIG_PATH = "config/repo_config.json" # 仓库配置文件地址

# 导入工具
class Importer:
    # 初始化
    def __init__(self, app_config):
        self.app_config = app_config
        self.support_languages = [] # 需要支持的语言
        self.keywords = [] # 关键字
        self.translates = {} # 翻译的词条
        self.entries = [] # 最终得到的翻译条目

    # 项目初始化的时候，导入 Android 翻译资源（values 文件夹根目录）
    def import_android_resources(self, dir_name):
        # 遍历解析 Android 资源目录
        xmlOperator = XmlOperator()
        for f in os.listdir(dir_name):
            language = ""
            if len(f) > 7:
                language = f[7:]
            else:
                language = "default"
            # 读取 xml 内容
            path = os.path.join(dir_name, f, "strings.xml")
            if not os.path.exists(path):
                logging.error("Language file not found : " + path)
                continue
            # 语言名称
            self.support_languages.append(language)
            dist = xmlOperator.read_android_resources(path)
            for k, v in dist.items():
                if k not in self.keywords:
                    self.keywords.append(k)
                if k not in self.translates:
                    self.translates[k] = {}
                self.translates[k][language] = v
        # 新增多语言的情况
        for sl in self.app_config.support_languages:
            if sl not in self.support_languages:
                for k, v in self.translates.items():
                    self.translates[k][sl] = ""
        # 输出用于调试的日志
        self.app_config.add_support_languages(self.support_languages)
        logging.debug(self.support_languages)
        logging.debug(self.keywords)
        logging.debug(self.translates)

    # 项目初始化的时候，导入 iOS 翻译资源（lproj 文件夹根目录）
    def import_ios_resources(self, dir_name):
        pass

    # 生成多语言仓库配置文件
    def gen_repo_config(self):
        json_obj = []
        for k, v in self.translates.items():
            json_obj.append({"keyword":k, "comment":"", "translates": v})
        logging.debug(json_obj)
        jsonOperator = JsonOperator()
        jsonOperator.write_json(REPO_CONFIG_PATH, json_obj)

    # 导入翻译 excel 文件，将翻译结果按照 keyword 写入配置文件
    def import_translated_excel(self, fname):
        pass

    # 比较改动的文件（传入 iOS 的资源文件）
    def compare_ios_keywords_change(self, fname):
        pass

    # 比较改动的文件（传入 Android 的资源文件）
    def compare_android_keywords_change(self, fname):
        pass
