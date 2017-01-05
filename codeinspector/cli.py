# -*- coding: utf-8 -*-

import json
import logging
logger = logging.getLogger(__name__)

import core
import utils
import inspector


def run():

    import argparse

    parser = argparse.ArgumentParser(prog='code-inspector', description='Python code inspector')
    parser.add_argument('path', nargs='+', help='the path to direcory or file with python code')
    args = parser.parse_args()

    for path in utils.iter_files(args.path):
        for node in inspector.Inspector(path).run():
            print(json.dumps(node))
