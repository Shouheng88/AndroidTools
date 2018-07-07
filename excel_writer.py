#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'WngShhng'

import xlwt

def write_excel(dist, languages):
    
    print('Beginning write resources to excel ......')

    # 创建 Excel 的工作簿
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)

    # 为每种类型的语言定义一个表单
    for language in languages:
        
        sheet = book.add_sheet(language, cell_overwrite_ok=True)

        # 写表头
        sheet.write(0, 0, '字符串名称')
        sheet.write(0, 1, '原义')
        sheet.write(0, 2, '翻译结果')

        # 写入字典到文件当中
        row = 1
        for k, v in dist.items():
            sheet.write(row, 0, k)
            sheet.write(row, 1, v)
            row += 1

        # 保存文件
        book.save(r'./Translate.xls') 
