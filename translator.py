#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'WngShhng'

import xml_reader as xr
import xml_writer as xw
import excel_writer as ew
import excel_reader as er

EXCEL_FILE_NAME = r'Translate.xls'
STRINGS_XML_FILE_NAME = r'strings.xml'

def create_translate_resources(dest, file=STRINGS_XML_FILE_NAME):
	'''
	根据传入的路径和想要生成的文件路径创建 Excel 
	dest 是想要生成的文件的前缀，比如你想要得到日文的，就输入 jp 等等
	file 是要进行翻译的文件的路径，默认会加载当前路径下面的 strings.xml 文件
	'''
	print("Beginning tranlate ......")
	# 从文件中读取字符串资源，存储到一个字典当中
	dist = xr.strings_reader(file)
	# 使用读取到的结果得到用于翻译的excel
	ew.write_excel(dist, dest)

def create_translated_resources(file=EXCEL_FILE_NAME, create_dir=True):
	'''根据传入的 Excel 文件路径来读取 Excel，默认会加载当前路径下面的 Translate.xls 文件'''
	# 读取翻译之后的字符串构成的字典，用字典来模拟各个表单
	dists = er.read_excel(file)
	# 将得到的所有数据写入到生成的各个翻译文件中
	xw.write_xmls(dists, create_dir)

def get_translate_status(file=EXCEL_FILE_NAME):
	'''检查当前的文件文件翻译状态'''
	# 读取翻译之后的字符串构成的字典，用字典来模拟各个表单
	dists = er.read_excel(file)
	result = {}
	for lang, dist in dists.items():
		total = len(dist)
		count = 0
		for v in dist.values():
			if v.strip() != '':
				count += 1
		result[lang] = count/total
	return result
