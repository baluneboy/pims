#!/usr/bin/env python
import time
import logging
import logging.config

def demo_rot():
    from os import path
    import glob
    import logging.handlers

    LOG_FILENAME = '/home/pims/log/logging_rotatingfile_example.out'
    
    # Set up a specific logger with our desired output level
    my_logger = logging.getLogger('MyLogger')
    my_logger.setLevel(logging.DEBUG)
    
    # Check if log exists and should therefore be rolled
    needRoll = False
    if path.isfile(LOG_FILENAME):
        needRoll = True
    
    # Add the log message handler to the logger
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, backupCount=9)
    
    my_logger.addHandler(handler)
    
    # This is a stale log, so roll it
    if needRoll:    
        # Add timestamp
        my_logger.debug('\n---------\nLog closed on %s.\n---------\n' % time.asctime())
    
        # Roll over on application start
        my_logger.handlers[0].doRollover()
    
    # Add timestamp
    my_logger.debug('\n---------\nLog started on %s.\n---------\n' % time.asctime())
    
    # Log some messages
    for i in range(20):
        my_logger.debug('i = %d' % i)
    
    # See what files are created
    logfiles = glob.glob('%s*' % LOG_FILENAME)
    
    for filename in logfiles:
        print filename

def demo_log_config():
    # set up logging
    logging.config.fileConfig('/home/pims/dev/programs/python/pims/files/log.conf')
    log = logging.getLogger('inputs')
    
    # log stuff
    for i in range(12):
        log.debug('debug message %03d' % i)
    log.info('info message')

    log = logging.getLogger('process')
    log.warn('warn message')
    log.error('error message')

    log = logging.getLogger('verify')
    log.critical('critical message')
    
    log.debug('Done %s.\n' % time.asctime() + '-'*99)
    
if __name__ == "__main__":
    demo_log_config()
