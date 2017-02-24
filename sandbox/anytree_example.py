#!/usr/bin/env python

from anytree import Node, RenderTree, NodeMixin

def simple_demo():
    top = Node('Top')
    marc = Node('Marc', parent=top)
    lian = Node('Lian', parent=marc)
    dan = Node('Dan', parent=top)
    jet = Node('Jet', parent=dan)
    jan = Node('Jan', parent=dan)
    
    today_tups = [ (1,11,111), (2,22,222), (3,33,333) ]
    joe = Node(today_tups, parent=jan)
    
    print top
    
    for pre, fill, node in RenderTree(top):
        #print '%s%s' % (pre, node.name)
        print node.name, type(node.name)
    
class MyBaseClass(object):
    foo  = 4
    
class MyClass(MyBaseClass, NodeMixin):
    
    def __init__(self, name, length, width, parent=None):
        super(MyClass, self).__init__()
        self.name = name
        self.length = length
        self.width = width
        self.parent = parent
        
my0 = MyClass('my0', 0, 0)
my1 = MyClass('my1', 1, 0, parent=my0)
my2 = MyClass('my2', 0, 2, parent=my0)

for pre, _, node in RenderTree(my0):
    treestr = u'%s%s' % (pre, node.name)
    print treestr, node.length, node.width