#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from repository import repository as repository
from file_operator import ExcelOperator as ExcelOperator
from file_operator import XmlOperator as XmlOperator
from file_operator import FileOperator as FileOperator
from config import TRANSLATE_EXCEL_SHEET_NAME
from config import TRANSLATE_EXCEL_FILE_NAME

# 文件生成工具类
class Generator:
    # 初始化
    def __init__(self, appConfig):
        self.appConfig = appConfig

    # 根据需要翻译的词条生成用于翻译的 excel
    def gen_translate_excel(self, output_dir):
        repository.load()
        dist = {}
        for data in repository.datas:
            # 增加词条列
            keyword = data["keyword"]
            if "Keyword" not in dist:
                dist["Keyword"] = []
            dist["Keyword"].append(keyword)
            # 增加翻译列
            translates = data["translates"]
            for k, v in translates.items():
                if k not in dist:
                    dist[k] = []
                dist[k].append(v)
        # 生成 Excel 文件
        excelOperator = ExcelOperator()
        out_file = os.path.join(self.appConfig.translate_excel_output_directory, TRANSLATE_EXCEL_FILE_NAME)
        excelOperator.write_excel(dist, out_file)
        return True

    # 生成 Android 多语言资源
    def gen_android_resources(self):
        repository.load()
        android_blacklist = self.appConfig.android_language_black_list
        xmlOperator = XmlOperator()
        for language in repository.languages:
            # 过滤黑名单
            if language in android_blacklist:
                continue
            dist = {}
            for data in repository.datas:
                keyword = data["keyword"]
                translates = data["translates"]
                translation = translates[language]
                dist[keyword] = translation
            # 写入资源
            language_dir = os.path.join(self.appConfig.android_resources_root_directory, "values-" + language)
            if not os.path.exists(language_dir):
                os.mkdir(language_dir)
            fname = os.path.join(language_dir, "strings.xml")
            xmlOperator.write_android_resources(dist, fname)

    # 生成 iOS 多语言资源
    def gen_ios_resources(self):
        repository.load()
        ios_blacklist = self.appConfig.ios_language_black_list
        fileOperator = FileOperator()
        for language in repository.languages:
            # 过滤黑名单
            if language in ios_blacklist:
                continue
            dist = {}
            for data in repository.datas:
                keyword = data["keyword"]
                translates = data["translates"]
                translation = translates[language]
                dist[keyword] = translation
            # 写入资源
            language_dir = os.path.join(self.appConfig.ios_resources_root_directory, language + ".lproj")
            if not os.path.exists(language_dir):
                os.mkdir(language_dir)
            fname = os.path.join(language_dir, "Localizable.strings")
            fileOperator.write_ios_resources(dist, fname)
