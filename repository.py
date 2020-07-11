
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from file_operator import JsonOperator as JsonOperator
from config import REPO_CONFIG_PATH

# 仓库加载
class Repository:
    # 初始化
    def __init__(self):
        self.datas = []
        self.keywords = []
        self.languages = []
        self.__loaded = False

    # 加载数据仓库
    def load(self):
        if self.__loaded:
            return
        jsonOperator = JsonOperator()
        self.datas = jsonOperator.read_json(REPO_CONFIG_PATH)
        for data in self.datas:
            self.keywords.append(data["keyword"])
            if len(self.languages) == 0:
                for k, v in data["translates"].items():
                    self.languages.append(k)
        self.__loaded = True
        logging.debug("Loaded keywords : " + str(self.keywords))
        logging.debug("Loaded languages : " + str(self.languages))

    # 尝试添加新的语言
    def try_to_add_new_language(self, language):
        if language not in self.languages:
            for data in self.datas:
                data["translates"].append({language, ""})
            logging.info("Language added : " + language)
            self.languages.append(language)
            return
        logging.info("Language exists : " + language)

    # 尝试添加新的词条
    def try_to_add_new_keyword(self, keyword, translation, language):
        if keyword not in self.keywords:
            translations = {}
            self.__init_keyword_translations(translation, translations, language)
            # 添加一个新的词条
            self.datas.append({"keyword": keyword, "comment": "", "translates": translations})
        else:
            # 判断词条是否发生了变更（之前调用 try_to_add_new_language 的时候处理了新增多语言的情况）
            for data in self.datas:
                if data["keyword"] == keyword:
                    old_translation = data["translates"][language]
                    if old_translation != translation:
                        self.__init_keyword_translations(translation, data["translates"], language)

    # 更新多语言词条
    def update_keyword(self, keyword, translation, language):
        for data in self.datas:
            if data["keyword"] == keyword:
                if language in data["translates"]:
                    data["translates"][language] = translation

    # 重新生成 repo json
    def rewrite_repo_json(self):
        jsonOperator = JsonOperator()
        jsonOperator.write_json(REPO_CONFIG_PATH, self.datas)

    # 获取仓库当前的状态
    def get_repo_state(self):
        self.load()
        missed_count = 0
        for data in self.datas:
            # 对每个词条进行处理
            for k, v in data["translates"].items():
                if len(v) == 0:
                    missed_count = missed_count + 1
                    break
        return {"missed_count": missed_count}

    # 获取用于翻译的多语言
    def get_keywords_to_translate(self):
        self.load()
        dist = {}
        for data in self.datas:
            keyword = data["keyword"]
            to_languages = []
            from_language = ""
            from_translation = ""
            for k,v in data["translates"].items():
                if len(v) == 0:
                    to_languages.append(k)
                else:
                    from_language = k
                    from_translation = v
            dist[keyword] = []
            for language in to_languages:
                dist[keyword].append({"translation":from_translation, "from":from_language, "to":language})
        return dist

    # 初始化词条的多语言
    def __init_keyword_translations(self, translation, translations, language):
        for l in self.languages:
            if l == language:
                translations[l] = translation
            else:
                translations[l] = ""

# The singleton repository
repository = Repository()
