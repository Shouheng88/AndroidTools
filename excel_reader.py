#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'WngShhng'

import xlrd

def read_excel(xlsfile):
    '''从指定的 Excel 中读取数据，返回一个字典，键是表单名，值是翻译之后的字典'''
    book = xlrd.open_workbook(xlsfile)
    dists = {}
    # 遍历所有的表单
    size = len(book.sheet_names())
    for i in range(size):
        sheet = book.sheet_by_index(i)
        dists[sheet.name] = read_sheet(sheet)
    return dists    

def read_sheet(sheet):
    '''读取每个表单中翻译之后的数据，返回一个字典'''
    nrows = sheet.nrows
    dist = {}
    for row in range(1, nrows):
        name = sheet.cell_value(row, 0)
        value = sheet.cell_value(row, 2)
        dist[name] = value
    return dist