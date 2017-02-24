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
    
class EeMeasure(MyBaseClass, NodeMixin):
    
    def __init__(self, name, values=None, parent=None):
        super(EeMeasure, self).__init__()
        self.name = name
        self.values = values
        self.parent = parent

ee0 = EeMeasure('VOLTS')

ee1 = EeMeasure('122-f02', parent=ee0) # no parent, so this is root node
me1 = EeMeasure('ref_zero', parent=ee1)
me2 = EeMeasure('plus5V',   parent=ee1)
today_tups = [ (1,11,111), (2,22,222), (3,33,333) ]
me2.values = today_tups

ee2 = EeMeasure('122-f03', parent=ee0) # no parent, so this is root node
me3 = EeMeasure('ref_zero', parent=ee2)
me4 = EeMeasure('plus5V',   parent=ee2)
today_tups = [ (1,11,111), (2,22,222), (3,33,333) ]
me3.values = today_tups

for pre, _, node in RenderTree(ee0):
    treestr = u'%s%s:' % (pre, node.name)
    print treestr, node.values

print me3.
