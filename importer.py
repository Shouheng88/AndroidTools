#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import json
from file_operator import ExcelOperator as ExcelOperator
from file_operator import XmlOperator as XmlOperator
from file_operator import JsonOperator as JsonOperator
from file_operator import FileOperator as FileOperator
from repository import repository as repository
from config import REPO_CONFIG_PATH
from config import TRANSLATE_EXCEL_SHEET_NAME

# 导入工具
class Importer:
    # 初始化
    def __init__(self, appConfig):
        self.appConfig = appConfig
        self.support_languages = [] # 需要支持的语言
        self.keywords = [] # 关键字
        self.translates = {} # 翻译的词条
        self.entries = [] # 最终得到的翻译条目

    # 项目初始化的时候，导入 Android 翻译资源（values 文件夹根目录）
    def import_android_resources(self):
        # 遍历解析 Android 资源目录
        xmlOperator = XmlOperator()
        for f in os.listdir(self.appConfig.android_resources_root_directory):
            language = self.__get_android_file_language(f)
            if len(language) <= 0:
                continue
            # 语言名称
            self.support_languages.append(language)
            path = os.path.join(self.appConfig.android_resources_root_directory, f, "strings.xml")
            dist = xmlOperator.read_android_resources(path)
            for k, v in dist.items():
                if k not in self.keywords:
                    self.keywords.append(k)
                if k not in self.translates:
                    self.translates[k] = {}
                self.translates[k][language] = v
        # 新增多语言的情况
        for sl in self.appConfig.support_languages:
            if sl not in self.support_languages:
                for k, v in self.translates.items():
                    self.translates[k][sl] = ""
        # 输出用于调试的日志
        self.appConfig.add_support_languages(self.support_languages)
        logging.debug("Parsed From Android Resources : " + str(self.support_languages))
        logging.debug("Parsed Keywords : " + str(self.keywords))
        logging.debug(self.translates)

    # 项目初始化的时候，导入 iOS 翻译资源（lproj 文件夹根目录）
    def import_ios_resources(self):
        fileOperator = FileOperator()
        for f in os.listdir(self.appConfig.ios_resources_root_directory):
            language = self.__get_ios_file_language(f)
            if len(language) <= 0:
                continue
            # 语言名称
            self.support_languages.append(language)
            path = os.path.join(self.appConfig.ios_resources_root_directory, f, "Localizable.strings")
            dist = fileOperator.read_ios_keywords(path)
            logging.debug("Read iOS keywords : " + str(dist))
            for k, v in dist.items():
                if k not in self.keywords:
                    self.keywords.append(k)
                if k not in self.translates:
                    self.translates[k] = {}
                self.translates[k][language] = v
        # 新增多语言的情况
        for sl in self.appConfig.support_languages:
            if sl not in self.support_languages:
                for k, v in self.translates.items():
                    self.translates[k][sl] = ""
        # 输出用于调试的日志
        self.appConfig.add_support_languages(self.support_languages)
        logging.debug("Parsed From iOS Resources : " + str(self.support_languages))
        logging.debug("Parsed Keywords : " + str(self.keywords))
        logging.debug(self.translates)

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
        # 读取 Excel
        excelOperator = ExcelOperator()
        dists = excelOperator.read_excel(fname)
        if TRANSLATE_EXCEL_SHEET_NAME in dists:
            # 加载仓库
            repository.load()
            col_list = dists.get(TRANSLATE_EXCEL_SHEET_NAME)
            # 获取所有的关键字
            keywords = []
            for row in range(1, len(col_list[0])):
                keyword = col_list[0][row]
                keywords.append(keyword)
            # 语言到词条映射
            for col in range(1, len(col_list)):
                language = ""
                translations = []
                for row in range(0, len(col_list[col])):
                    value = col_list[col][row]
                    if row == 0:
                        language = value
                    else:
                        translations.append(value)
                # 词条对应起来
                for j in range(0, len(keywords)):
                    keyword = keywords[j]
                    translation = translations[j]
                    # 更新到仓库
                    repository.update_keyword(keyword, translation, language)
            # 重写 repo json
            repository.rewrite_repo_json()
        logging.debug(dists)

    # 比较改动的文件
    def update_ios_resource(self):
        repository.load()
        pass

    # 比较改动的文件
    def update_android_resource(self):
        repository.load()
        # 解析指定的多语言路径中的词条
        xmlOperator = XmlOperator()
        for f in os.listdir(self.appConfig.android_resources_root_directory):
            language = self.__get_android_file_language(f)
            if len(language) <= 0:
                continue
            # 语言名称
            repository.try_to_add_new_language(language)
            path = os.path.join(self.appConfig.android_resources_root_directory, f, "strings.xml")
            # 词条新增 or 变更
            dist = xmlOperator.read_android_resources(path)
            for k, v in dist.items():
                repository.try_to_add_new_keyword(k, v, language)
        # 重写 repo json
        repository.rewrite_repo_json()

    # Android：从文件名中获取文件的多语言
    def __get_android_file_language(self, f):
        language = ""
        if len(f) > 7:
            language = f[7:] # values-xx
        else:
            language = "default"
        # 读取 xml 内容
        path = os.path.join(self.appConfig.android_resources_root_directory, f, "strings.xml")
        if not os.path.exists(path):
            logging.error("Language file not found : " + path)
            language = ""
        return language

    # iOS：从文件名中获取文件的多语言
    def __get_ios_file_language(self, f):
        language = ""
        if len(f) > 5:
            language = f[0:-6]
        else:
            language = "default"
        path = os.path.join(self.appConfig.ios_resources_root_directory, f, "Localizable.strings")
        if not os.path.exists(path):
            logging.error("Language file not found : " + path)
            language = ""
        return language
