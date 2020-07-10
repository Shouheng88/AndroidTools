#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from repository import repository as repository
from file_operator import ExcelOperator as ExcelOperator
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
        pass

    # 生成 iOS 多语言资源
    def gen_ios_resources(self):
        pass
