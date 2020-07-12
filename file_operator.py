#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xml.dom.minidom import parse
import xml.dom.minidom
import logging
import json
import xlwt
import os
import codecs
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
        dist = {}
        try:
            DOMTree = xml.dom.minidom.parse(fname)
        except Exception:
            logging.error("Failed to read Android resources : " + fname)
            return dist
        collection = DOMTree.documentElement
        # 读取所有 string 标签
        strings = collection.getElementsByTagName("string")
        # 将读取到的所有元素拼接成字典列表
        index = 0
        for string in strings:
            index += 1
            try:
                keyword = string.getAttribute('name')
                translation = ""
                if len(string.childNodes) == 1:
                    node = string.childNodes[0]
                    # CDATA 特殊处理
                    if node.nodeType == 4:
                        translation = "<![CDATA[" + str(node.data) + "]]>"
                    else:
                        translation = node.data
                else:
                    # 对子节点遍历，将所有对子节点拼接起来
                    for node in string.childNodes:
                        # CDATA 特殊处理
                        if node.nodeType == 4:
                            translation = translation + "<![CDATA[" + str(node.data) + "]]>"
                        else:
                            translation = translation + node.toxml()
                # 过滤处理
                if '\\\'' in translation:
                    translation = translation.replace('\\\'', '\'')
                dist[keyword] = translation
            except BaseException as e:
                logging.error("Invalid entry at index " + str(index) + " " + str(keyword) + " : " + str(e))
        # 返回解析结果
        logging.debug("Read Android resources \"" + fname + "\" end.")
        return dist

    # 将 Android 的 xml 资源写入到文件中
    def write_android_resources(self, dist, fname):
        logging.debug("Writing Android resources " + fname + " : " + str(dist))
        content = '<resources>\n'
        for k, v in dist.items():
            # 处理 '
            if '\'' in v:
                v = v.replace("\'", "\\\'")
            # 处理 > 和 <
            if ('>' in v or '<' in v) and '<![CDATA[' not in v and '<br' not in v and '<b' not in v and '<a' not in v and '<i' not in v and '<u' not in v and '<em' not in v and '<big' not in v and '<small' not in v and '<h' not in v:
                v = v.replace('>', '&gt;')
                v = v.replace('<', '&lt;')
            # 处理 …
            if '…' in v and '<![CDATA[' not in v:
                v = v.replace('…', '&#8230;')
            # 拼接
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

# 文件操作类，用于 iOS 文件操作
class FileOperator:
    # 初始化
    def __init__(self):
        pass

    # 读取 iOS 词条
    def read_ios_keywords(self, fname):
        logging.debug("Reading ios keywrods : " + fname)
        dist = {}
        with open(fname, 'r') as f:
            # 读取每一行的数据
            ls = [line.strip() for line in f]
            f.close()
            for l in ls:
                sps = l.split("=")
                keyword = sps[0].strip()[1:-1]
                translation = sps[1].strip()[1:-2]
                dist[keyword] = translation
        return dist

    # 生成 iOS 的多语言资源
    def write_ios_resources(self, dist, fname):
        logging.debug("Writing iOS resources " + fname + " : " + str(dist))
        content = ''
        for k, v in dist.items():
            content = content + "\"" + k + "\" = \"" + v + "\";\n"
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(content)

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
