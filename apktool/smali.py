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

import os, sys, time, logging
from typing import List
sys.path.insert(0, '../')
import global_config
from files.textfiles import read_text
from files.jsonfiles import write_json

DEFAULT_MAX_TRACEBACK_GENERATION = 3
DEFAULT_RESULT_OUTPUT_PATH = "."

class SmaliSearcherConfiguration:
    '''The smali searcher configuration.'''
    def __init__(self) -> None:
        self.package = ''
        # The methods to search for example 'Ljava/lang/StringBuilder;-><init>()V', or keyword to search.
        self.keywords = []
        self.apk_md5 = ''
        self.traceback = TracebackConfiguration()
        self.output = DEFAULT_RESULT_OUTPUT_PATH
        self.start_time = int(time.time())

    def __str__(self) -> str:
        return "SmaliSearcherConfiguration [%s][%s][%s][%s][%s]" \
            % (self.package, self.keywords, self.methods, \
                str(self.traceback), self.result_store_path)

    def cost_time(self) -> str:
        '''Return and calculate the cost time.'''
        cost = int(time.time()) - self.start_time
        return "%d:%d" % (cost/60, cost%60)

class TracebackConfiguration:
    '''The traceback configuration.'''
    def __init__(self) -> None:
        self.enable = True
        self.generation = DEFAULT_MAX_TRACEBACK_GENERATION

    def __str__(self) -> str:
        return "TracebackConfiguration [%s][%s]" % (str(self.enable), str(self.generation))

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
                json_obj["keywords"][k].append(item.pattern)
        # Prepare methods json map.
        for k, items in self.methods.items():
            for item in items:
                item.calculate_pattern(configuration)
                if k not in json_obj["methods"]:
                    json_obj["methods"][k] = []
                json_obj["methods"][k].append(item.pattern)
        # Return json object.
        return json_obj

    def to_methods(self, configuration: SmaliSearcherConfiguration):
        '''Get all methods for json output.'''
        json_obj = []
        patterns = []
        for items in self.methods.values():
            for item in items:
                item.calculate_pattern(configuration)
                if item.pattern not in patterns:
                    patterns.append(item.pattern)
                    json_obj.append(item.pattern)
        return json_obj

def search_smali(dir: str, configuration: SmaliSearcherConfiguration=None):
    '''
    Search in given directory.
    - dir: the directory for smali files, such as 'workspace_1637821369/smali_mix'
    - configuration: the smali searcher configuration
    '''
    # Filt by package name.
    filted_dirs = _filt_by_packages(dir, configuration)
    logging.info("After filt by package: " + str(filted_dirs))
    # Search in smali files by depth visit.
    for filted_dir in filted_dirs:
        search_by_depth_visit(filted_dir, configuration)

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
                    print(" >>> Searching [%s][%d] under [%s] " % (configuration.cost_time(), \
                        searched, path.removeprefix(dir)), end = '\r')
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

def _filt_by_packages(dir: str, configuration: SmaliSearcherConfiguration=None) -> List[str]:
    '''Filt directories by package name.'''
    dirs = []
    # All directories are valid under given directory if the package is not configured.
    if configuration is None or len(configuration.package) == 0:
        dirs.append(dir)
        return dirs
    # Filt directories by package name.
    package = configuration.package.replace(".", "/")
    logging.debug("Start to file for package [%s] under [%s]." % (package, dir))
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

def _write_result_to_json(result: SmaliSercherResult, configuration: SmaliSearcherConfiguration=None):
    '''Write result to json file.'''
    result_dir = "%s/results_%s_%d" % (configuration.output, configuration.apk_md5, int(time.time()))
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    # Write methods mapping file.
    jsob_obj = result.to_json(configuration)
    f_name = "%s/smali_mappings.json" % result_dir
    write_json(f_name, jsob_obj)
    # Write methods json file.
    jsob_obj = result.to_methods(configuration)
    f_name = "%s/smali_methods.json" % result_dir
    write_json(f_name, jsob_obj)
    # Write method stack json file.
    jsob_obj = _compose_method_stacktrace(result, configuration)
    f_name = "%s/smali_stacks.json" % result_dir
    write_json(f_name, jsob_obj)

def _compose_method_stacktrace(result: SmaliSercherResult, configuration: SmaliSearcherConfiguration=None):
    '''Compose method stacktrace.'''
    json_obj = {}
    # Prepare keywords json map.
    for k, items in result.keywords.items():
        for item in items:
            item.calculate_pattern(configuration)
            if k not in json_obj:
                json_obj[k] = []
            json_obj[k].append(item.pattern)
    patterns = []
    # Prepare methods json map.
    for k, items in result.methods.items():
        for item in items:
            item.calculate_pattern(configuration)
            if item.pattern not in patterns:
                patterns.append(item.pattern)
                if item.pattern not in json_obj:
                    json_obj[item.pattern] = []
                json_obj[item.pattern].append(item.pattern)
                if k not in json_obj:
                    json_obj[item.pattern].append(k)
                else:
                    json_obj[item.pattern].extend(json_obj[k])
    # Return json object.
    return json_obj

def _anything_need_to_search(configuration: SmaliSearcherConfiguration=None) -> bool:
    '''To judge is there anything necessary to search.'''
    return len(configuration.keywords) > 0

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

def _search_keyword_under_given_file(path: str, content: str, result: SmaliSercherResult, configuration: SmaliSearcherConfiguration=None):
    '''Search keyword under given file based on text search.'''
    lines = content.split("\n")
    for keyword in configuration.keywords:
        if content.find(keyword) > 0:
            method_region = False
            for line in lines:
                # Found method region.
                if line.startswith(".method"):
                    method = SmaliMethod()
                    method_region = True
                    method.path = path
                    method.method_name = line.removeprefix(".method").strip()
                    method.private = line.startswith(".method private")
                elif line.startswith(".end method"):
                    method_region = False
                # Add method to result.
                if line.find(keyword) > 0:
                    if method_region and method.method_name != '':
                        logging.debug("Found keyword usage: %s" % str(method))
                        result.keywords[keyword].append(method)
                        if method.private:
                            _search_private_method_usage_under_current_file(path, content, method, result, configuration)
                    else:
                        logging.error("Found one isolate keyword in [%s][%s]" % (path, line))

def _search_private_method_usage_under_current_file(path: str, content: str, to_search: SmaliMethod,\
     result: SmaliSercherResult, configuration: SmaliSearcherConfiguration=None):
    '''Search private method usage in current file.'''
    to_search.calculate_pattern(configuration)
    logging.debug("Search private method under current file for: %s" % (str(to_search.pattern)))
    lines = content.split("\n")
    method_region = False
    for line in lines:
        # Find method region.
        if line.startswith(".method"):
            method = SmaliMethod()
            method_region = True
            method.path = path
            method.method_name = line.removeprefix(".method").strip()
            method.private = line.startswith(".method private")
        elif line.startswith(".end method"):
            method_region = False
        # Add method to result.
        if line.find(to_search.pattern) > 0:
            if method_region and method.method_name != '':
                # Clear method region flag.
                method_region = False
                logging.debug("Found method usage: %s" % str(method))
                if result.methods.get(to_search.pattern) == None:
                    result.methods[to_search.pattern] = []
                result.methods[to_search.pattern].append(method)
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
    for methods in result.methods.values():
        for method in methods:
            if not method.private:
                method.prepare_for_traceback(configuration)
                visit_methods.append(method)
    # Continusly visit the tree.
    circle = 0
    while len(visit_methods) > 0 and circle < configuration.traceback.generation:
        visits = [dir]
        searched = 0
        circle = circle+1
        # Add the max traceback generation judgement to avoid traceback too much.
        while len(visits) > 0 and len(visit_methods) > 0:
            visit = visits.pop()
            if os.path.exists(visit):
                for f in os.listdir(visit):
                    path = os.path.join(visit, f)
                    if os.path.isdir(path):
                        visits.append(path)
                    elif not _should_ignore_given_file(path):
                        searched = searched + 1
                        print(" >>> Traceback [%s][%d][%d][%d][%d] under [%s] " % (configuration.cost_time(),\
                             circle, searched, len(visit_methods), total, path.removeprefix(dir)), end = '\r')
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
    private_visited_pattern = []
    for visit in visit_methods:
        # Increase traceback count and remove if it was visited a circle.
        visit.traceback_count = visit.traceback_count+1
        if visit.traceback_count > total:
            methods.remove(visit)
            logging.debug("Remove traceback method %s" % str(visit))
            # Skip
            continue
        if visit.pattern not in result.methods:
            result.methods[visit.pattern] = []
        # Find usage for method.
        if content.find(visit.pattern) > 0:
            method_region = False
            for line in lines:
                # Find method region.
                if line.startswith(".method"):
                    method = SmaliMethod()
                    method_region = True
                    method.path = path
                    method.method_name = line.removeprefix(".method").strip()
                    method.private = line.startswith(".method private")
                elif line.startswith(".end method"):
                    method_region = False
                # Add method to result. Should ignore method signature line.
                if line.find(visit.pattern) > 0:
                    if method_region and method.method_name != '':
                        # Clear method region state: if the 'visit' was called twice or more in current method, 
                        # only keep one method record.
                        method_region = False
                        logging.debug("Found traceback method usage of %s in %s" % (str(visit), str(method)))
                        result.methods[visit.pattern].append(method)
                        # Add to traceback methods to search continusly if it's not private.
                        if not method.private:
                            method.prepare_for_traceback(configuration)
                            # Add judgement to avoid visit the same method twice.
                            if method.pattern not in result.methods:
                                methods.append(method)
                                # Anyway, add one map to methods if the pattern is visited. Used to avoid multiple times visit.
                                result.methods[method.pattern] = []
                        else:
                            # Need to avoid same private method visited multiple times.
                            if method.method_name not in private_visited_pattern:
                                private_visited_pattern.append(method.method_name)
                                # TODO methods calling private method might need to be added to 'methods' to traceback.
                                _search_private_method_usage_under_current_file(path, content, method, result, configuration)
                    else:
                        logging.error("Found one isolate method usage in [%s][%s]" % (path, line))

if __name__ == "__main__":
    '''Program entrance.'''
    global_config.config_logging('../log/app.log')
    configuration = SmaliSearcherConfiguration()
    # print(configuration.traceback)
    # print(configuration)
    # configuration.methods = []
    search_smali("workspace_1637821369/smali_mix", configuration)
    # search_under_smali("workspace_1637821369/smali_classes3", configuration)
    # search_by_depth_visit('workspace_1637821369/smali_mix/com/netease/cloudmusic', configuration)
    # method = SmaliMethod()
    # method.method_name = "private static getChannel(I)Ljava/lang/String;"
    # method.path = "workspace_1637821369/smali_mix/com/netease/cloudmusic/statistic/encrypt/StatisticConfigFactory.smali"
    # method.prepare_for_traceback(configuration)
    # print(str(method))
    # list = [1, 2, 3, 4]
    # for item in list:
    #     list.append(5)
    # print(list)
