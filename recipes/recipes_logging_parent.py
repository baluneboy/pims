#!/usr/bin/env python

"""We can define and configure a parent logger in one module and create (but not
configure) a child logger in a separate module.  Then, all logger calls to the
child will pass up to the parent.

THIS IS MAIN MODULE THAT CONFIGURES PARENT LOGGER (AUX. MODULE IS COMPANION FILE)."""

import logging
import auxiliary_module

def main():
    
    # create logger with 'spam_application'
    logger = logging.getLogger('spam_application')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('spam.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)d %(name)s %(levelname)s %(message)s',datefmt='%Y-%m-%d,%H:%M:%S')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    logger.info('creating an instance of auxiliary_module.Auxiliary')
    a = auxiliary_module.Auxiliary()
    logger.info('created an instance of auxiliary_module.Auxiliary')
    logger.info('calling auxiliary_module.Auxiliary.do_something')
    a.do_something()
    logger.info('finished auxiliary_module.Auxiliary.do_something')
    logger.info('calling auxiliary_module.some_function()')
    auxiliary_module.some_function()
    logger.info('done with auxiliary_module.some_function()')
    
if __name__ == '__main__':
    main()