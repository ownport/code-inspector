# -*- coding: utf-8 -*-

import sys

PY2 = sys.version_info < (3, 0)
PY32 = sys.version_info < (3, 3)    # Python 2.5 to 3.2
PY33 = sys.version_info < (3, 4)    # Python 2.5 to 3.3
PY34 = sys.version_info < (3, 5)    # Python 2.5 to 3.4
try:
    sys.pypy_version_info
    PYPY = True
except AttributeError:
    PYPY = False

try:
    import ast
except ImportError:     # Python 2.5
    import _ast as ast


if PY2:
    def getNodeType(node):
        # workaround str.upper() which is locale-dependent
        return str(unicode(node.__class__.__name__).upper())
else:
    def getNodeType(node):
        return node.__class__.__name__.upper()


class Node(object):

    def __init__(self, node, source):

        self._node = node
        self._source = source

    @property
    def origin(self):
        return self._node

    @property
    def name(self):
        if hasattr(self._node, 'id'):     # One of the many nodes with an id
            return self._node.id
        if hasattr(self._node, 'name'):   # an ExceptHandler node
            return self._node.name

    @property
    def type(self):
        return getNodeType(self._node)

    @property
    def source(self):
        return self._source

    @property
    def lineno(self):
        return self._node.lineno if self._node.lineno else None

    @property
    def fields(self):
        return [f for f in ast.iter_fields(self._node)]

    @property
    def children(self):
        return [c for c in ast.iter_child_nodes(self._node)]

    @property
    def details(self):
        return {
            'name': self.name,
            'type': self.type,
            'source': self.source,
            'lineno': self.lineno,
            'fields': [str(f) for f in self.fields],
            'children': [str(c) for c in self.children],
        }

    def __str__(self):
        return "%s [%d] %s, %s" % (self.source, self.lineno, self.type, self.name)



class ImportNode(Node):

    @property
    def aliases(self):

        return [{'name': a.name, 'asname': a.asname} for a in self._node.names]

    @property
    def module(self):

        level = getattr(self._node, 'level', None)
        module = getattr(self._node, 'module', '')
        return  ('.' * level) + (module or '') if level else module

    @property
    def details(self):

        _details = super(ImportNode, self).details
        _details['module'] = self.module
        _details['aliases'] = self.aliases
        return _details

    def __str__(self):

        if not self.module:
            for a in self.aliases:
                if a['asname']:
                    return 'import %s as %s' % (a['name'], a['asname'])
                else:
                    return 'import %s' % a['name']
        else:
            for a in self.aliases:
                if a['asname']:
                    return 'from %s import %s as %s' % (self.module, a['name'], a['asname'])
                else:
                    return 'from %s import %s' % (self.module, a['name'])


class FunctionNode(Node):

    def __str__(self):
        return "%s()" % (self.name,)


class ClassNode(Node):

    @property
    def bases(self):
        result = list()
        for b in self._node.bases:
            base_node = Node(b, self.source)
            if base_node.type == 'ATTRIBUTE':
                result.append('.'.join([base_node.origin.value.id, base_node.origin.attr]))
            else:
                result.append(base_node.name or base.type)
        return result

    @property
    def keywords(self):
        if not PY2:
            return [Node(k, self.source) for k in self._node.keywords]
        else:
            return []

    @property
    def statements(self):
        return [Node(s, self.source) for s in self._node.body]

    @property
    def methods(self):

        return [FunctionNode(s, self.source)
                    for s in self._node.body
                        if Node(s, self.source).type == 'FUNCTIONDEF']

    @property
    def decorators(self):
        return [d for d in self._node.decorator_list]

    @property
    def details(self):

        _details = super(ClassNode, self).details
        _details['bases'] = [str(b) for b in self.bases]
        _details['keywords'] = self.keywords
        _details['statements'] = [str(s) for s in self.statements]
        _details['methods'] = [str(s) for s in self.methods]
        return _details
