#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'WngShhng'

import xlrd
import xlwt
from xlutils.copy import copy

import logging

import baidu_api.baidu_translate_api as api

current_working_sheet = ''
current_working_row_number = 0

TOTAL_TRANSLATE_COUNT = 10

MAP_KEY_SHEET_ROW = 'sheet_row'
MAP_KEY_ORIGINAL = 'original'
MAP_KEY_TRANSLATED = 'translated'

def auto_translate(xlsfile):
    '''使用三方 api 自动翻译 Excel 中的字符串'''
    map_to_translate = get_map_to_translate(xlsfile)
    translate(map_to_translate)
    write_to_excel(xlsfile, map_to_translate)

def write_to_excel(xlsfile, map_to_translate):
    '''将翻译之后的内容写入到 Excel 中'''
    logging.debug(map_to_translate)
    book = xlrd.open_workbook(xlsfile)
    wb = copy(book)
    for sheet_name, queue in map_to_translate.items():
        for element in queue:
            ws = wb.get_sheet(sheet_name)
            ws.write(element[MAP_KEY_SHEET_ROW], 2, element[MAP_KEY_TRANSLATED])
    wb.save(xlsfile) 

def translate(map_to_translate):
    '''翻译传入的队列中的元素，并返回翻译之后的队列'''
    logging.debug(map_to_translate)
    index = 0
    for sheet_name, queue in map_to_translate.items():
        for element in queue:
            translated = api.translate(element[MAP_KEY_ORIGINAL], sheet_name)
            element[MAP_KEY_TRANSLATED] = translated
            index += 1
            print('%d个词条已翻译'%index)
    return map_to_translate

def get_map_to_translate(xlsfile):
    '''遍历Excel找到需要翻译的元素，组成一个队列返回'''
    book = xlrd.open_workbook(xlsfile)
    size = len(book.sheet_names())
    trans_map = {}
    count = 0
    for i in range(size):
        sheet = book.sheet_by_index(i)
        nrows = sheet.nrows
        for row in range(1, nrows):
            original = sheet.cell_value(row, 1)
            translated = sheet.cell_value(row, 2)
            if translated == '':
                count += 1
                try: 
                    trans_map[sheet.name] 
                except KeyError:
                    trans_map[sheet.name] = []
                trans_map[sheet.name].append(get_queue_element(row, original, translated))
            if count == TOTAL_TRANSLATE_COUNT:
                break
        if count == TOTAL_TRANSLATE_COUNT:
            break
    return trans_map

def get_queue_element(sheet_row, original, translated):
    '''根据传入的参数获取一个用于翻译的队列的元素'''
    return {
        MAP_KEY_SHEET_ROW: sheet_row,
        MAP_KEY_ORIGINAL: original,
        MAP_KEY_TRANSLATED: translated,
    }