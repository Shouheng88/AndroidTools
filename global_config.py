#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

def config_logging(filename: str = 'app.log'):
    '''Config loggin library globaly.'''
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    logging.basicConfig(filename=filename, filemode='a', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    logging.FileHandler(filename=filename, encoding='utf-8')
