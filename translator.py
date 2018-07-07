#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'WngShhng'

import xml_reader as xr
import xml_writer as xw
import excel_writer as ew
import excel_reader as er


# 根据指定的文件资源，创建一个用于翻译的 Excel 表格
def createTranslateResources():

	print("Beginning tranlate ......")

	# 从文件中读取字符串资源，存储到一个字典当中
	dist = xr.strings_reader('strings.xml')

	# 测试 xml 解析结果
	# for k,v in dist.items():
	# 	print(k + ':' + v)

	# 使用读取到的结果得到用于翻译的excel
	ew.write_excel(dist, ['fr', 'zh', 'jp', 'Zh-en'])



# 根据指定的翻译之后的 Excel 资源自动生成各种语言的字符串文件
def createTranslatedResources():
	
	dsits = er.read_excel(r'./Translate.xls')
	
	xw.write_xmls(dsits, True)


createTranslatedResources()



