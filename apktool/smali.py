#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
/////////////////////////////////////////........................
//                                       ........................
//    The Android Smali File Searcher    ........................
//                                       ........................
//    @Author Shouheng Wang              ........................
//                                       ........................
/////////////////////////////////////////........................
'''

import os, sys, time, shutil, logging
from typing import List
sys.path.insert(0, '../')
import global_config
from files.textfiles import read_text
from files.jsonfiles import read_json, write_json

SMALI_MIX_DIRECTORY = "smali_mix"
SMALI_SEARCHER_CONFIGURATION_FILE = "config.json"

class SmaliSearcherConfiguration:
    '''The smali searcher configuration.'''
    def __init__(self) -> None:
        self.package = ''
        self.keywords = []
        # The methods to search, like 'Ljava/lang/StringBuilder;-><init>()V'
        self.methods = []
        self.traceback = True
        self.result_store_path = "."
    
    def __str__(self) -> str:
        return "SmaliSearcherConfiguration [%s][%s][%s][%s][%s]" \
            % (self.package, self.keywords, self.methods, \
                str(self.traceback), self.result_store_path)

class SmaliMethod: 
    '''Smali method wrapper class.'''
    def __init__(self) -> None:
        self.method_name = ''
        self.private = True
        self.path = ''
        self.traceback_count = 0
        self.pattern = ''
    
    def prepare_for_traceback(self, configuration: SmaliSearcherConfiguration):
        '''Prepare the smali method.'''
        # To avoid multiple calculation.
        if self.pattern != '':
            return
        # Calculate method pattern.
        h_index = self.path.find(configuration.package)
        r_index = self.path.find(".smali")
        if h_index >= 0 and r_index >= 0:
            cls = self.path[h_index:r_index]
            n_index = self.method_name.rfind(' ')
            name = self.method_name[n_index+1:]
            self.pattern = "L%s;->%s" % (cls, name)
        else:
            logging.error("Illegal traceback method: %s" % str(self))

    def calculate_pattern(self, configuration: SmaliSearcherConfiguration):
        '''Calculate pattern.'''
        self.prepare_for_traceback(configuration)

    def __str__(self) -> str:
        return "SmaliMethod [%s][%s][%s][%s][%d]" % (str(self.private), \
            self.method_name, self.path, self.pattern, self.traceback_count)

class SmaliSercherResult:
    '''The smali searcher result.'''
    def __init__(self) -> None:
        self.keywords = {}
        self.methods = {}

    def prepare(self, configuration: SmaliSearcherConfiguration):
        '''Prepare the result object.'''
        for keyword in configuration.keywords:
            self.keywords[keyword] = []
        for method in configuration.methods:
            self.methods[method] = []

    def to_json(self, configuration: SmaliSearcherConfiguration):
        '''Transfer object to json.'''
        json_obj = {
            "keywords": {},
            "methods": {}
        }
        # Prepare keywords json map.
        for k, items in self.keywords.items():
            for item in items:
                item.calculate_pattern(configuration)
                if k not in json_obj["keywords"]:
                    json_obj["keywords"][k] = []
                json_obj["keywords"][k].append({k: item.pattern})
        # Prepare methods json map.
        for k, items in self.methods.items():
            for item in items:
                item.calculate_pattern(configuration)
                if k not in json_obj["methods"]:
                    json_obj["methods"][k] = []
                json_obj["methods"][k].append({k: item.pattern})
        # Return json object.
        return json_obj

def decompile(apk: str = None):
    '''Decompile the APK.'''
    out = "./workspace_%d" % int(time.time())
    os.system("sh ../bin/apktool/apktool.sh D %s -o %s" % (apk, out))
    return out

def search_smali(dir: str, configuration: SmaliSearcherConfiguration=None):
    '''
    Search in given directory.
    - dir: the directory for smali files, such as 'workspace_1637821369/smali_mix'
    - configuration: the smali searcher configuration
    '''
    files = os.listdir(dir)
    smalis = []
    for f in files:
        if f.startswith("smali") and f != SMALI_MIX_DIRECTORY:
            # search_under_smali(os.path.join(dir, f), configuration)
            smalis.append(os.path.join(dir, f))
    logging.info("Mixing " + str(smalis))
    _mix_all_smalis(dir, smalis)
    # Filt by package name.
    filted = _filt_by_packages(dir, configuration)
    logging.info("After filt by package: " + str(filted))
    # Search in smali files by depth visit.
    search_by_depth_visit(dir, configuration)

def search_by_depth_visit(dir: str, configuration: SmaliSearcherConfiguration=None):
    '''Search keywords by depth visit.'''
    result = SmaliSercherResult()
    result.prepare(configuration)
    visits = [dir]
    searched = 0
    while len(visits) > 0 and _anything_need_to_search(configuration):
        visit = visits.pop()
        if os.path.exists(visit):
            for f in os.listdir(visit):
                path = os.path.join(visit, f)
                if os.path.isdir(path):
                    visits.append(path)
                elif not _should_ignore_given_file(path):
                    searched = searched + 1
                    print(" >>> Searching [%d] under [%s] " % (searched, path), end = '\r')
                    _search_under_given_file(path, result, configuration)
    # Traceback usages: find where these methods all called.
    if configuration.traceback:
        _traceback_keyword_usages(dir, result, searched, configuration)
    # Write searched result to json file.
    _write_result_to_json(result, configuration)

def transfer_method(package: str, cls: str, method: str) -> str:
    '''
    Transfer method of given class from code style to smali call style.
    For example, to transfer method of pacakge 'java.lang', class name 'StringBuilder'
    and method name 'StringBuilder()' to 'Ljava/lang/StringBuilder;-><init>()V'.
    TODO complete the transformation method later.
    '''
    f_package = package.replace('.', '/')
    return 'L%s/%s;->' % (f_package, cls)

def _read_configuration() -> SmaliSearcherConfiguration:
    '''Read smali searcher configuration.'''
    json_object = read_json(SMALI_SEARCHER_CONFIGURATION_FILE)
    configuration = SmaliSearcherConfiguration()
    configuration.package = json_object["package"]
    configuration.keywords = json_object["keywords"]
    configuration.methods = json_object["methods"]
    configuration.traceback = json_object["traceback"]
    return configuration

def _filt_by_packages(dir: str, configuration: SmaliSearcherConfiguration=None) -> List[str]:
    '''Filt directories by package name.'''
    dirs = []
    # All directories are valid under given directory if the package is not configured.
    if configuration is None or len(configuration.package) == 0:
        dirs.append(dir)
        return dirs
    # Filt directories by package name.
    package = configuration.package
    visits = [dir]
    while len(visits) > 0:
        visit = visits.pop()
        if os.path.exists(visit):
            for f in os.listdir(visit):
                path = os.path.join(visit, f)
                # Need to remove prefix to match the package name.
                valid = path.removeprefix(dir + "/")
                if os.path.isdir(path) and package.startswith(valid):
                    if package == valid:
                        dirs.append(path)
                    else:
                        visits.append(path)
    return dirs

def _mix_all_smalis(dir: str, smalis: List[str]):
    '''
    Mix all smali directories to one to reduce the complexity of the alogrithm.
    Also we can make a more interesting things based on mixed smalis.
    '''
    to = os.path.join(dir, SMALI_MIX_DIRECTORY)
    progress = 1
    for smali in smalis:
        print(" >>> Mixing [%s] %d%%" % (smali, progress*100/len(smalis)), end = '\r')
        logging.info(" >>> Mixing [%s] %d%%" % (smali, progress*100/len(smalis)))
        try:
            shutil.copytree(smali, to, dirs_exist_ok=True)
        except shutil.Error as e:
            for src, dst, msg in e.args[0]:
                print(dst, src, msg)
        progress = progress + 1

def _write_result_to_json(result: SmaliSercherResult, configuration: SmaliSearcherConfiguration=None):
    '''Write result to json file.'''
    jsob_obj = result.to_json(configuration)
    f_name = "smali_result_%d.json" % int(time.time())
    write_json(f_name, jsob_obj)

def _anything_need_to_search(configuration: SmaliSearcherConfiguration=None) -> bool:
    '''To judge is there anything necessary to search.'''
    return len(configuration.methods) > 0 and len(configuration.keywords) > 0

def _should_ignore_given_file(path: str, configuration: SmaliSearcherConfiguration=None) -> bool:
    '''
    Should ignore given file. Ignore given file to accelerate search progress.
    Add more judgements for yourself to custom this operation.
    '''
    parts = os.path.split('/')
    if len(parts) > 0:
        f_name = parts[len(parts)-1]
        if f_name.startswith("R$"):
           return True 
    return False

def _search_under_given_file(path: str, result: SmaliSercherResult, configuration: SmaliSearcherConfiguration=None):
    '''Search under given file.'''
    content = read_text(path)
    _search_keyword_under_given_file(path, content, result, configuration)
    _search_method_usage_under_given_file(path, content, result, configuration)

def _search_keyword_under_given_file(path: str, content: str, result: SmaliSercherResult, configuration: SmaliSearcherConfiguration=None):
    '''Search keyword under given file based on text search.'''
    lines = content.split("\n")
    for keywrod in configuration.keywords:
        if content.find(keywrod) > 0:
            method_region = False
            method = SmaliMethod()
            for line in lines:
                # Found method region.
                if line.startswith(".method"):
                    method_region = True
                    method.path = path
                    method.method_name = line.removeprefix(".method").strip()
                    method.private = line.startswith(".method private")
                elif line.startswith(".end method"):
                    method_region = False
                # Add method to result.
                if line.find(keywrod) > 0:
                    if method_region and method.method_name != '':
                        # TODO search usages in current file if the method is private
                        logging.debug("Found keyword usage: %s" % str(method))
                        result.keywords[keywrod].append(method)
                    else:
                        logging.error("Found one isolate keyword in [%s][%s]" % (path, line))

def _search_method_usage_under_given_file(path: str, content: str, result: SmaliSercherResult, configuration: SmaliSearcherConfiguration=None):
    '''Search method usage under given file.'''
    lines = content.split("\n")
    for keywrod in configuration.methods:
        if content.find(keywrod) > 0:
            method_region = False
            method = SmaliMethod()
            for line in lines:
                # Find method region.
                if line.startswith(".method"):
                    method_region = True
                    method.path = path
                    method.method_name = line.removeprefix(".method").strip()
                    method.private = line.startswith(".method private")
                elif line.startswith(".end method"):
                    method_region = False
                # Add method to result.
                if line.find(keywrod) > 0:
                    if method_region and method.method_name != '':
                        # TODO search usages in current file if the method is private
                        logging.debug("Found method usage: %s" % str(method))
                        result.methods[keywrod].append(method)
                    else:
                        logging.error("Found one isolate method usage in [%s][%s]" % (path, line))

def _traceback_keyword_usages(dir: str, result: SmaliSercherResult, total: int, configuration: SmaliSearcherConfiguration=None):
    '''Traceback keyword usages.'''
    # Prepare methods list for traceback.
    visit_methods = []
    for methods in result.keywords.values():
        for method in methods:
            if not method.private:
                method.prepare_for_traceback(configuration)
                visit_methods.append(method)
    # Continusly visit the tree.
    circle = 0
    while len(visit_methods) > 0:
        visits = [dir]
        searched = 0
        circle = circle+1
        logging.debug("Traceback methods: %s" % _connect_visit_methods(visit_methods))
        while len(visits) > 0 and len(visit_methods) > 0:
            visit = visits.pop()
            if os.path.exists(visit):
                for f in os.listdir(visit):
                    path = os.path.join(visit, f)
                    if os.path.isdir(path):
                        visits.append(path)
                    elif not _should_ignore_given_file(path):
                        searched = searched + 1
                        print(" >>> Traceback [%d][%d][%d][%d] under [%s] " % (circle, searched, len(visit_methods), total, path), end = '\r')
                        _traceback_methods_usages(path, visit_methods, result, total, configuration)

def _connect_visit_methods(methods: List[SmaliMethod]) -> str:
    '''Connect visit methods.'''
    ret = ''
    for method in methods:
        ret = ret + ' ' + str(method)
    return ret

def _traceback_methods_usages(path: str, methods: List[SmaliMethod], result: SmaliSercherResult, total: int, configuration: SmaliSearcherConfiguration=None):
    '''Traceback methods usages.'''
    content = read_text(path)
    lines = content.split("\n")
    visit_methods = []
    visit_methods.extend(methods)
    for visit in visit_methods:
        # Increase traceback count and remove if it was visited a circle.
        visit.traceback_count = visit.traceback_count+1
        if visit.traceback_count > total:
            methods.remove(visit)
            logging.debug("Remove trace method %s" % str(visit))
        # Find usage for method.
        if content.find(visit.pattern) > 0:
            method_region = False
            method = SmaliMethod()
            for line in lines:
                # Find method region.
                if line.startswith(".method"):
                    method_region = True
                    method.path = path
                    method.method_name = line.removeprefix(".method").strip()
                    method.private = line.startswith(".method private")
                elif line.startswith(".end method"):
                    method_region = False
                # Add method to result.
                if line.find(visit.pattern) > 0:
                    if method_region and method.method_name != '':
                        logging.debug("Found traceback method usage: %s" % str(method))
                        if result.methods.get(visit.pattern) == None:
                            result.methods[visit.pattern] = []
                            result.methods[visit.pattern].append(method)
                        # Add to traceback methods to search continusly if it's not private.
                        # TODO search usages in current file if the method is private
                        if not method.private:
                            method.prepare_for_traceback(configuration)
                            methods.append(method)
                    else:
                        logging.error("Found one isolate method usage in [%s][%s]" % (path, line))

if __name__ == "__main__":
    '''Program entrance.'''
    global_config.config_logging('../log/app.log')
    # decompile("/Users/wangshouheng/Desktop/apkanalyse/app_.apk")
    configuration = _read_configuration()
    # print(configuration.traceback)
    # print(configuration)
    # configuration.methods = []
    # search_smali("workspace_1637821369/" + SMAILI_MIX_DIRECTORU, configuration)
    # search_under_smali("workspace_1637821369/smali_classes3", configuration)
    search_by_depth_visit('workspace_1637821369/smali_mix/com/netease/cloudmusic', configuration)
    # method = SmaliMethod()
    # method.method_name = "private static getChannel(I)Ljava/lang/String;"
    # method.path = "workspace_1637821369/smali_mix/com/netease/cloudmusic/statistic/encrypt/StatisticConfigFactory.smali"
    # method.prepare_for_traceback(configuration)
    # print(str(method))
    # list = [1, 2, 3, 4]
    # for item in list:
    #     list.append(5)
    # print(list)
