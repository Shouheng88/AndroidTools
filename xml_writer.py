#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'WngShhng'

import os
import shutil

def write_xmls(dsits, create_dir):
    # 将从 Excel 中读取到的内容写入到 xml 文件中
    for con, dist in dsits.items():
        write_xml(con, dist, create_dir)


def write_xml(file_appendix, dist, create_dir):
    # 根据是否要创建目录来获取要创建的文件的路径
    file_path = ''
    if create_dir:
        dir_name = 'values-' + file_appendix
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
        os.mkdir(dir_name)
        file_path = dir_name + '/' + 'strings.xml'
    else:
        file_path = 'strings' + file_appendix + '.xml'

    # 拼接要写入到文件中的内容
    content = '<resources>\n'
    for k, v in dist.items():
        content += '\t<string name="' + k + '">' + v + '</string>\n'
    content += '</resources>'

    # 将内容写入到文件中
    with open(file_path, 'w') as f:
        f.write(content)
 