
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
            self.languages.append(language)
            logging.debug("Tring to add new language " + language + " into " + str(self.datas))
            for data in self.datas:
                data["translates"][language] = ""
            logging.info("Language added : " + language)
            return
        logging.info("Language exists : " + language)

    # 尝试添加新的词条
    def try_to_add_new_keyword(self, keyword, translation, language):
        if keyword not in self.keywords:
            # 添加一个新的词条
            translations = {}
            self.__init_keyword_translations(translation, translations, language)
            self.datas.append({"keyword": keyword, "comment": "", "translates": translations})
            self.keywords.append(keyword)
        else:
            # 判断词条是否发生了变更（之前调用 try_to_add_new_language 的时候处理了新增多语言的情况）
            for data in self.datas:
                if data["keyword"] == keyword:
                    old_translation = data["translates"][language]
                    # 应该过滤掉 old_translation 为空掉情况，此时说明它已经被处理过了，没必要再次处理
                    # 所以这就意味着不要一次更改两个多语言文件的同一词条，因为我们通过词条变更来确定哪些词条的多语言需要重新翻译，
                    # 如果同时修改，那么只能以多语言文件列表的第一个文件的改动为准，因此造成结果不可预知
                    # 建议通过导出 Excel 的方式，通过修改 Excel 并重新导入到项目中的方式来导入自己翻译的多语言
                    if old_translation != translation and len(old_translation) != 0:
                        logging.debug("Found translation change for : " + keyword + " (" + language + ").")
                        self.__init_keyword_translations(translation, data["translates"], language)
                    # 处理完毕，找到一个就可以结束了
                    break

    # 修改词条
    def try_ro_modify_keyword(self, keyword, translation, language):
        # 不存在的语言不支持修改
        if language not in self.languages:
            return
        # 遍历更新
        for data in self.datas:
            if data["keyword"] == keyword and language in data["translates"]:
                if data["translates"][language] != translation:
                    data["translates"][language] = translation
                break

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
