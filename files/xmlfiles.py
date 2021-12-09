#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xml.dom.minidom import parse
import xml.dom.minidom
import logging

def read_android_strings(fname):
    '''Read android languages.'''
    dist = {}
    try:
        # Use minidom to open xml.
        DOMTree = xml.dom.minidom.parse(fname)
    except Exception:
        logging.error("Failed to read Android strings: " + fname)
        return dist
    collection = DOMTree.documentElement
    strings = collection.getElementsByTagName("string")
    index = 0
    for string in strings:
        index += 1
        try:
            keyword = string.getAttribute('name')
            translation = ""
            if len(string.childNodes) == 1:
                node = string.childNodes[0]
                # Handle CDATA label.
                if node.nodeType == 4:
                    translation = "<![CDATA[" + str(node.data) + "]]>"
                else:
                    translation = node.data
            else:
                # Handle child nodes.
                for node in string.childNodes:
                    # Handle CDATA label.
                    if node.nodeType == 4:
                        translation = translation + "<![CDATA[" + str(node.data) + "]]>"
                    else:
                        translation = translation + node.toxml()
            # Do filter for some chars.
            if '\\\'' in translation:
                translation = translation.replace('\\\'', '\'')
            dist[keyword] = translation
        except BaseException as e:
            logging.error("Invalid entry at index " + str(index) + " " + str(keyword) + " : " + str(e))
    return dist

def write_android_resources(dist, fname):
    '''Write android string resources.'''
    content = '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
    for k, v in dist.items():
        # Handle chars etc.
        if '\'' in v:
            v = v.replace("\'", "\\\'")
        # Handle > and <
        if ('>' in v or '<' in v) and '<![CDATA[' not in v and '<br' not in v and '<b' not in v and \
            '<a' not in v and '<i' not in v and '<u' not in v and '<em' not in v and \
            '<big' not in v and '<small' not in v and '<h' not in v:
            v = v.replace('>', '&gt;')
            v = v.replace('<', '&lt;')
        # Handle …
        if '…' in v and '<![CDATA[' not in v:
            v = v.replace('…', '&#8230;')
        # Connnect.
        content += '    <string name="' + k + '">' + v + '</string>\n'
    content += '</resources>'
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(content)
