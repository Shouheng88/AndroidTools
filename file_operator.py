#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xml.dom.minidom import parse
import xml.dom.minidom
import logging
import json
import xlwt
import os
import xlrd
from config import TRANSLATE_EXCEL_SHEET_NAME

# Xml 操作类
class XmlOperator:
    # 初始化
    def __init__(self):
        pass

    # 读取 Android 的 xml 资源（当前只支持读取 string 标签）
    def read_android_resources(self, fname):
        logging.debug("Reading Android resources of \"" + fname + "\"")
        # 使用 minidom 解析器打开 XML 文档
        DOMTree = xml.dom.minidom.parse(fname)
        collection = DOMTree.documentElement
        # 读取所有 string 标签
        strings = collection.getElementsByTagName("string")
        # 将读取到的所有元素拼接成字典列表
        dist = {}
        index = 0
        for string in strings:
            index += 1
            if string.hasAttribute('name'):
                dist[string.getAttribute('name')] = string.childNodes[0].data
            else:
                raise Exception('Invliad string definition at index : ', index)
        # 返回解析结果
        logging.debug("Read Android resources \"" + fname + "\" end.")
        return dist

    # 将 Android 的 xml 资源写入到文件中
    def write_android_resources(self, dist, fname):
        logging.debug("Writing Android resources " + fname + " : " + str(dist))
        content = '<resources>\n'
        for k, v in dist.items():
            content += '    <string name="' + k + '">' + v + '</string>\n'
        content += '</resources>'
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(content)

# Json 操作类
class JsonOperator:
    # 初始化
    def __init__(self):
        pass

    # 写入 json 到文件
    def write_json(self, fname, json_obj):
        json_str = json.dumps(json_obj)
        with open(fname, "w") as f:
            f.write(json_str)

    # 从文件读取 json 字符串
    def read_json(self, fname):
        with open(fname, "r") as f:
            return json.load(f)

# Excel 操作类
class ExcelOperator:
    # 初始化
    def __init__(self):
        pass

    # 写 Excel
    # TODO 这里到 sheet name 应该从 dist 中读取，下面这样不具备通用性
    def write_excel(self, dist, file):
        # 创建 Excel 的工作簿
        book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        sheet = book.add_sheet(TRANSLATE_EXCEL_SHEET_NAME, cell_overwrite_ok=True)
        # dist : {"a":[], "b":[], "c": []}
        row_count = 0
        col_count = 0
        for k, v in dist.items():
            sheet.write(row_count, col_count, k)
            for item in v:
                row_count = row_count + 1
                sheet.write(row_count, col_count, item)
            col_count = col_count + 1
            row_count = 0
        book.save(file)

    # 读取 Excel，{sheet_name:[[col 1], [col 2], []]}
    def read_excel(self, xlsfile):
        dists = {}
        book = xlrd.open_workbook(xlsfile)
        size = len(book.sheet_names())
        for i in range(size):
            sheet = book.sheet_by_index(i)
            dists[sheet.name] = self.__read_sheet(sheet)
        return dists

    # 读取 Excel Sheet
    def __read_sheet(self, sheet):
        col_list = []
        # 按列遍历
        for col in range(0, sheet.ncols):
            col_list.append([])
            # 按行遍历
            for row in range(0, sheet.nrows):
                value = sheet.cell_value(row, col)
                col_list[col].append(value)
        return col_list
