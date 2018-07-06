#!/usr/bin/python
# -*- coding: UTF-8 -*-

from xml.dom.minidom import parse
import xml.dom.minidom

import xlwt

import xlrd

def translate():
	print("Beginning tranlate......")

	# 使用minidom解析器打开 XML 文档
	DOMTree = xml.dom.minidom.parse("strings.xml")
	collection = DOMTree.documentElement
	
	strings = collection.getElementsByTagName("string")

	for string in strings:
		# print(string.childNodes[0].data)
		pass

def createExcel():
	print('Beginning create excel......')

	book = xlwt.Workbook(encoding='utf-8', style_compression=0)

	sheet = book.add_sheet('test', cell_overwrite_ok=True)

	sheet.write(0, 0, 'EnglishName')  # 其中的'0-行, 0-列'指定表中的单元，'EnglishName'是向该单元写入的内容
	sheet.write(1, 0, 'Marcovaldo')

	txt1 = '中文名字'
	sheet.write(0, 1, txt1)  # 此处需要将中文字符串解码成unicode码，否则会报错
	txt2 = '马可瓦多'
	sheet.write(1, 1, txt2)

	book.save(r'./test1.xls') 

def readExcel():
	xlsfile = r"./test1.xls" 			# 打开指定路径中的xls文件
	book = xlrd.open_workbook(xlsfile) 	# 得到Excel文件的book对象，实例化对象

	sheet0 = book.sheet_by_index(0) 	# 通过sheet索引获得sheet对象
	print(sheet0)						# 输出sheet对象
	print("==========")

	sheet_name = book.sheet_names()[0]	# 获得指定索引的sheet表名字
	print(sheet_name)
	print("==========")

	sheet1 = book.sheet_by_name(sheet_name)	# 通过sheet名字来获取，当然如果知道sheet名字就可以直接指定
	nrows = sheet0.nrows    				# 获取行总数
	print(nrows)
	print("==========")

	for i in range(nrows) :
		print(sheet1.row_values(i))
	print("==========")

	ncols = sheet0.ncols
	print(ncols)
	print("==========")

	row_data = sheet0.row_values(0)
	print(row_data)
	print("==========")

	col_data = sheet0.col_values(0) 
	print(col_data)
	print("==========")

	cell_value1 = sheet0.cell_value(0, 0)
	print(cell_value1)
	print("==========")

	cell_value2 = sheet0.cell_value(0, 1)
	print(cell_value2)
	print("==========")

readExcel()



