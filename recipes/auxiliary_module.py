#!/usr/bin/env python

"""We can define and configure a parent logger in one module and create (but not
configure) a child logger in a separate module.  Then, all logger calls to the
child will pass up to the parent.

THIS IS AUXILIARY MODULE THAT CREATES CHILD LOGGER"""

import logging

# create logger
module_logger = logging.getLogger('spam_application.auxiliary')

class Auxiliary:
    def __init__(self):
        self.logger = logging.getLogger('spam_application.auxiliary.Auxiliary')
        self.logger.info('creating an instance of Auxiliary')
    def do_something(self):
        self.logger.info('doing something')
        a = 1 + 1
        self.logger.info('done doing something')

def some_function():
    module_logger.info('received a call to "some_function"')