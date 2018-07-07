#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'WngShhng'

import xlrd

# 从指定的 Excel 中读取数据，返回一个字典
# 键是表单名，值是翻译之后的字典
def read_excel(xlsfile):
    # 读取 Excel 工作簿
    book = xlrd.open_workbook(xlsfile)

    dists = {}
    
    # 遍历所有的表单
    size = len(book.sheet_names())
    for i in range(1, size):
        sheet = book.sheet_by_index(i)
        dists[sheet.name] = read_sheet(sheet)

    return dists    


# 读取每个表单中翻译之后的数据，返回一个字典
def read_sheet(sheet):
    nrows = sheet.nrows

    dist = {}
    for row in range(1, nrows):
        name = sheet.cell_value(row, 0)
        value = sheet.cell_value(row, 2)
        dist[name] = value
    
    return dist