#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xml.dom.minidom import parse
import xml.dom.minidom
import logging
import json

# Xml 操作类
class XmlOperator:
    # 初始化
    def __init__(self):
        pass

    # 读取 Android 的 xml 资源（当前只支持读取 string 标签）
    def read_android_resources(self, fname):
        logging.debug("Reading Android resources of \"" + fname + "\"")
        # 使用 minidom 解析器打开 XML 文档
        DOMTree = xml.dom.minidom.parse(fname)
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
        # 返回解析结果
        logging.debug("Read Android resources \"" + fname + "\" end.")
        return dist

    # 将 Android 的 xml 资源写入到文件中
    def write_android_resources(self, fname, dist):
        pass

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
