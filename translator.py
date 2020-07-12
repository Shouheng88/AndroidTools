#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import hashlib
import logging
import json
import time
from config import API_URL
from config import BAIDU_CONFIG_URL
from repository import repository

# 百度翻译工具类
class BaiduTranslator:
    # 初始化
    def __init__(self):
        self.mappings = {} # 语言映射表
        self.reversed_mappings = {} # 反向语言映射表
        self.appid = "" # 文字识别 AppId
        self.secret = "" # 文字识别 App Secret
        self.__load_configs() # 加载配置文件

    # 将指定的字符串翻译为指定的语言（传入的 language 应当是 App 多语言缩写）
    def translate(self, words, language):
        try:
            mapped_language = self.__get_mapped_language(language)
            if mapped_language == None:
                logging.warning("Missed language mapping \"" + language + "\"")
                return ""
            translated = self.translate_directly(words, mapped_language)
            # 返回一个字典，包含翻译结果和映射的多语言
            return {"translation":translated, "mapped_language":mapped_language}
        except KeyError as ke:
            logging.error("Unknown language " + language + " : " + ke)
            return ""

    # 将指定的字符串翻译为指定的语言（传入的 mapped_language 就是 baidu 平台定义的语言缩写）
    def translate_directly(self, words, mapped_language):
        logging.info("Translate \"" + words + "\" to \"" + mapped_language + "\".")
        form_data = self.__get_post_form_data(words, mapped_language)
        # 增加一点延时
        time.sleep(1)
        response = requests.post(API_URL, form_data)
        result = response.json()
        try:
            translated = result["trans_result"][0]["dst"]
            logging.info("Translated \"" + words + "\" to \"" + translated + "\".")
            return translated
        except KeyError:
            logging.error("Translate error " + result["error_code"] + " " + result["error_msg"])
            return ""

    # 获取方向的语言映射列表，比如 香港和澳门的繁体都是繁体，此时可以用这个映射，避免重复翻译
    def get_reversed_mapped_languages(self, from_language):
        return self.reversed_mappings.get(from_language)

    # 判断是否配置完成
    def is_configed(self):
        return self.appid != "your_app_id" and self.secret != "your_app_secret"

    # 获取指定的语言对应的 Baidu 翻译语言参数
    def __get_mapped_language(self, language):
        return self.mappings.get(language)

    # 加载配置文件
    def __load_configs(self):
        with open(BAIDU_CONFIG_URL) as fp:
            data = json.load(fp)
            logging.debug(data["mappings"])
            self.mappings = data["mappings"]
            self.appid = data["app_id"]
            self.secret = data["app_secret"]
            # 构建反向的多语言映射
            for k,v in self.mappings.items():
                if v not in self.reversed_mappings:
                    self.reversed_mappings[v] = []
                self.reversed_mappings[v].append(k)

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

# 翻译工具类
class Translator:
    # 初始化
    def __init__(self):
        pass

    # 开始翻译
    def start_translate(self, progress_callback, finish_callback):
        repository.load()
        translator = BaiduTranslator()
        dist = repository.get_keywords_to_translate()
        logging.debug("Dist to translate : " + str(dist))
        total = len(dist)
        count = 0
        # 遍历词条
        translated_languages = []
        for keyword,v in dist.items():
            logging.debug("Translating " + keyword)
            # 清空标记
            translated_languages.clear()
            for item in v:
                # from_language = item["from"]
                to_language = item["to"]
                translation = item["translation"]
                if to_language in translated_languages:
                    continue
                # 可能已经被翻译过了
                result = translator.translate(translation, to_language)
                if len(result) != 0:
                    translated = result["translation"]
                    mapped_language = result["mapped_language"]
                    # 反向的映射关系填充翻译结果
                    reversed_mappings = translator.get_reversed_mapped_languages(mapped_language)
                    logging.debug("Get reversed mappings for " + mapped_language + " : " + str(reversed_mappings))
                    for reversed_mapping in reversed_mappings:
                        # 标记方向映射列表，更新词条信息
                        translated_languages.append(reversed_mapping)
                        repository.update_keyword(keyword, translated, reversed_mapping)
                else:
                    logging.warning("One keyword missed to translate : " + keyword)
            # 回调
            count = count + 1
            progress_callback(count * 100 / total)
        # 重写 repo json
        repository.rewrite_repo_json()
        finish_callback()
