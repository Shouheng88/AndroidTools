#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def read_text(fname) -> str:
    '''Read text file full content.'''
    with open(fname, 'r') as f:
        content = f.read()
        f.close()
    return content
