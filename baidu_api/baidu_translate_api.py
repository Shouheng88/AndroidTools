#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import hashlib
import logging

import baidu_api.baidu_translate_config as config

def translate(to_translate, to_language):
    '''翻译指定的文字为指定的语言'''
    try:
        logging.debug('to ' + to_language + ' : ' + to_translate)
        language = get_language_mapping(to_language)
        logging.debug(language)
        from_data = get_post_form_data(to_translate, language)
        logging.debug(from_data)
        response = requests.post(config.TRANSLATE_URL, from_data)
        result = response.json()
        logging.debug(result)
        try:
            return result['trans_result'][0]['dst']
        except KeyError:
            print(result['error_code'] + ' : ' + result['error_msg'])
            return ''
    except KeyError:
        print('不支持该语言: ' + to_language)
        return ''

def get_language_mapping(language):
    '''获取语言的映射，需要从Android的命名方式映射到百度支持的文字'''
    return config.MAPPING[language]

def get_post_form_data(to_translate, to_language):
    '''获取用于发送post的form数据'''
    dist = {}
    dist['q'] = to_translate
    dist['from'] = 'auto'
    dist['to'] = to_language
    dist['appid'] = config.APP_ID
    salt = '12321321'
    dist['salt'] = salt
    sign = config.APP_ID + to_translate + salt + config.APP_SECRET 
    logging.debug(sign)
    hl = hashlib.md5()
    hl.update(sign.encode(encoding='utf-8'))
    md5_result = hl.hexdigest()
    dist['sign'] = md5_result
    return dist

# print(translate('我的名字是什么', 'en-rUS'))
