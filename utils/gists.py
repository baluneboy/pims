#!/usr/bin/env python

import json
import collections

def tree():
    """return tree structure whose default values are themselves trees
       a hierarchy/structure where only leaf nodes hold values

    >>> sensors = tree()
    >>> sensors['121f02']['day 1'] = ['too', 'to']
    >>> sensors['121f03']['day 1'] = ['tree', 'treat', 'treaty']
    >>> sensors['121f02']['day 2'] = ['toot', 'tot']
    >>> print json.dumps(sensors, sort_keys=True, indent=3, separators=(',', ':'))
    {
       "121f02":{
          "day 1":[
             "too",
             "to"
          ],
          "day 2":[
             "toot",
             "tot"
          ]
       },
       "121f03":{
          "day 1":[
             "tree",
             "treat",
             "treaty"
          ]
       }
    }
    
    """
    # see https://gist.github.com/hrldcpr/2012250
    
    return collections.defaultdict(tree)

def add_tree_value(t, path, value):
    """add value to tree structure's path > leaf node
    
    >>> sensors = tree()
    >>> sensors['121f02']['day 1'] = ['f1', 'f2']
    >>> sensors['121f03']['day 1'] = ['f1', 'f2', 'f3']
    >>> sensors['121f02']['day 2'] = ['f11', 'f22']
    >>> add_tree_value(sensors, '121f02>day 3'.split('>'), ["file 1", "file 2"])
    >>> print json.dumps(sensors, sort_keys=True, indent=3, separators=(',', ':'))
    {
       "121f02":{
          "day 1":[
             "f1",
             "f2"
          ],
          "day 2":[
             "f11",
             "f22"
          ],
          "day 3":{
             "day 3":[
                "file 1",
                "file 2"
             ]
          }
       },
       "121f03":{
          "day 1":[
             "f1",
             "f2",
             "f3"
          ]
       }
    }
    
    """
    for node in path:
        t = t[node]
    t[node] = value
    
    
if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
