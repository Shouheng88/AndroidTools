#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import hashlib
import logging
import json

API_URL = 'http://api.fanyi.baidu.com/api/trans/vip/translate' # 百度语音识别 API

# 百度翻译工具类
class BaiduTranslator:
    # 初始化
    def __init__(self):
        self.mappings = {} # 语言映射表
        self.appid = "" # 文字识别 AppId
        self.secret = "" # 文字识别 App Secret
        self.__load_configs() # 加载配置文件

    # 将指定的字符串翻译为指定的语言（传入的 language 应当是 App 多语言缩写）
    def translate(self, words, language):
        try:
            logging.info("Translate " + words + " to " + language + " .")
            mapped_language = self.__get_mapped_language(language)
            return self.translate_directly(words, mapped_language)
        except KeyError as ke:
            logging.error("Unknown language " + language + " : " + ke)
            return ""

    # 将指定的字符串翻译为指定的语言（传入的 mapped_language 就是 baidu 平台定义的语言缩写）
    def translate_directly(self, words, mapped_language):
        logging.info("Translate \"" + words + "\" to \"" + mapped_language + "\".")
        form_data = self.__get_post_form_data(words, mapped_language)
        response = requests.post(API_URL, form_data)
        result = response.json()
        try:
            translated = result["trans_result"][0]["dst"]
            logging.info("Translated \"" + words + "\" to \"" + translated + "\".")
            return translated
        except KeyError:
            logging.error("Translate error " + result["error_code"] + " " + result["error_msg"])
            return ""

    # 获取指定的语言对应的 Baidu 翻译语言参数
    def __get_mapped_language(self, language):
        return self.mappings[language]

    # 加载配置文件
    def __load_configs(self):
        with open("config/baidu_api_config.json") as fp:
            data = json.load(fp)
            logging.debug(data["mappings"])
            self.mappings = data["mappings"]
            self.appid = data["app_id"]
            self.secret = data["app_secret"]

    # 获取用于发送的 post form 数据
    def __get_post_form_data(self, words, language):
        dist = {}
        dist['q'] = words
        dist['from'] = 'auto'
        dist['to'] = language
        dist['appid'] = self.appid
        salt = '12321321'
        dist['salt'] = salt
        sign = self.appid + words + salt + self.secret
        hl = hashlib.md5()
        hl.update(sign.encode(encoding='utf-8'))
        md5_result = hl.hexdigest()
        dist['sign'] = md5_result
        return dist
