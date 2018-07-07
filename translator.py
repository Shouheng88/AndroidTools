#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'WngShhng'

import xml_reader as xr
import excel_writer as ew
import excel_reader as er

import xlrd

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
	for res_name, dist in dsits.items():
		print(res_name)
		for k,v in dist.items():
			print(k + ':' + v)

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

createTranslatedResources()



