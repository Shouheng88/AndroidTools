#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def write_json(path, json_obj):
    '''Write json object to json file.'''
    json_str = json.dumps(json_obj)
    with open(path, "w") as f:
        f.write(json_str)

def read_json(path):
    '''Read json object from json file.'''
    with open(path, "r") as f:
        return json.load(f)
