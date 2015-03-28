#!/usr/bin/env python
"""
Shelve variables can be useful during debug.
"""

import shelve

class MyShelf(object):
    
    def __init__(self, filename='/tmp/shelve.out'):
        self.filename = filename
        
    def save_vars(self, vars):
        my_shelf = shelve.open(self.filename, 'n') # 'n' for new
        for key in vars:
            try:
                my_shelf[key] = vars[key]
            except TypeError:
                # __builtins__, my_shelf, and imported modules can not be shelved.
                print('ERROR shelving: {0}'.format(key))
        my_shelf.close()        

    def load_all(self):
        d = {}
        my_shelf = shelve.open(self.filename)
        for key in my_shelf:
            if not isinstance(my_shelf[key], MyShelf):
                d[key] = my_shelf[key]
        my_shelf.close()
        return d
        
def demo():
    T = 'Hiya'
    val = [1,2,3,'boo']
    ms = MyShelf()
    ms.save_vars( locals() )
    
if __name__ == "__main__":
    demo()