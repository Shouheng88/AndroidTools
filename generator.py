#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 文件生成工具类
class Generator:
    # 初始化
    def __init__(self):
        pass

    # 根据需要翻译的词条生成用于翻译的 excel
    def gen_translate_excel(self):
        pass

    # 生成 Android 多语言资源
    def gen_android_resources(self):
        pass

    # 生成 iOS 多语言资源
    def gen_ios_resources(self):
        pass

    # 生成多语言资源
    def gen_resources(self):
        self.gen_android_resources()
        self.gen_ios_resources()

