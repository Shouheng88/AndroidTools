#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'WngShhng'

from xml.dom.minidom import parse
import xml.dom.minidom

def strings_reader(path):
    
    print('Begin to parse ' + path + ' ......')

    # 使用minidom解析器打开 XML 文档
    DOMTree = xml.dom.minidom.parse(path)
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

    print('Successfully parsed ' + path + ' ......')

    # 返回解析结果
    return dist