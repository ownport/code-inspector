# -*- coding: utf-8 -*-

import os
import sys

import logging
logger = logging.getLogger(__name__)

try:
    import ast
except ImportError:     # Python 2.5
    import _ast as ast

import nodes


class Inspector(object):

    def __init__(self, path):

        if not os.path.exists(path):
            raise IOError('The path to file does not exist, %s' % path)
        self._path = path

        # in Python 2.6, compile() will choke on \r\n line endings. In later
        # versions of python it's smarter, and we want binary mode to give
        # compile() the best opportunity to do the right thing WRT text
        # encodings.
        if sys.version_info < (2, 7):
            mode = 'rU'
        else:
            mode = 'rb'

        with open(path, mode) as f:
            _source = f.read()

        if sys.version_info < (2, 7):
            _source += '\n'     # Workaround for Python <= 2.6

        self._tree = ast.parse(_source, self._path)
        self._num_lines = sum(1 for _ in _source.split('\n'))


    def run(self):

        cursor = 0
        prev_node = None

        for node in nodes.Node(self._tree, self._path).children:
            node = nodes.Node(node, self._path)
            if node.type in ('IMPORT', 'IMPORTFROM'):
                node = nodes.ImportNode(node.origin, self._path)
            elif node.type in ('CLASSDEF', ):
                node = nodes.ClassNode(node.origin, self._path)

            if cursor == 0:
                cursor = node.lineno
                prev_node = node
                continue
            elif cursor < node.lineno:
                details = prev_node.details
                details['offset'] = node.lineno - cursor
                cursor = node.lineno
                prev_node = node
                yield details

        if prev_node and cursor < self._num_lines:
            details = prev_node.details
            details['offset'] = self._num_lines - cursor + 1
            yield details
