import datetime
import logging
#import logging.handlers

class SimpleLog(object):
    """a simple log object"""
    
    def __init__(self, log_basename, log_path='/tmp', log_level='DEBUG'):
        logFormatter = logging.Formatter("%(asctime)s %(threadName)-12.12s %(levelname)-5.5s %(message)s")
        log = logging.getLogger('pims.files.log')
        log.setLevel( getattr(logging, log_level.upper()) )
        fileHandler = logging.FileHandler("{0}/{1}.log".format(log_path, log_basename))
        fileHandler.setFormatter(logFormatter)
        log.addHandler(fileHandler)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        log.addHandler(consoleHandler)
        self.log = log

#log = SimpleLog('trash').log
#log.info('trashlog starting')
#raise SystemExit

def init_log(log_file):
    
    # Basic config
    logging.basicConfig(filename=log_file, filemode='w', level=logging.DEBUG, format='%(asctime)s,%(name)s,%(levelname)s,%(message)s')

    # Define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    ## Add rotating log message handler to the logger
    #rot_file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=9)

    # Set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-9s: %(levelname)-8s: %(message)s')

    # Tell the handler to use this format
    console.setFormatter(formatter)

    # Add handler to the root logger
    logging.getLogger('').addHandler(console)

    # Now, we can log to the root logger, or any other logger. First the root...
    logging.info('Logging started at %s.', datetime.datetime.now() )

    # Now, define a couple of other loggers which represent areas in this app:
    log_inputs = logging.getLogger('INPUTS')
    log_process = logging.getLogger('PROCESS')
    log_verify = logging.getLogger('VERIFY')

    ## Add each to handler
    #log_inputs.addHandler(rot_file_handler)
    #log_process.addHandler(rot_file_handler)
    #log_verify.addHandler(rot_file_handler)

    return log_inputs, log_process, log_verify

class HandbookLog(object):
    def __init__(self, log_file='/home/pims/log/handbook.log'):
        self.file = log_file
        self.inputs, self.process, self.verify = init_log(log_file)

class PadLog(object):
    def __init__(self, log_file='/home/pims/log/pad.log'):
        self.inputs, self.process, self.verify = init_log(log_file)

class OssbtmfBackfillRoadmapsLog(object):
    def __init__(self, log_file='/home/pims/log/ossbtmfbackfillroadmaps.log'):
        self.inputs, self.process, self.verify = init_log(log_file)

class TrashLog(object):
    def __init__(self, log_file='/home/pims/log/trash.log'):
        self.inputs, self.process, self.verify = init_log(log_file)
        
def demo_log(log_file='/tmp/demo_pdfjam.log'):
    
    logging.basicConfig(filename=log_file, filemode='w', level=logging.DEBUG, format='%(asctime)s,%(name)s,%(levelname)s,%(message)s')

    # Define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    # Set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-9s: %(levelname)-8s: %(message)s')

    # Tell the handler to use this format
    console.setFormatter(formatter)

    # Now, we can log to the root logger, or any other logger. First, the root...
    logging.info('Logging started now at %s', datetime.datetime.now() )

    # Now, define a couple of other loggers which might represent areas in your application:
    logDemo = logging.getLogger('DEMO')

    return logDemo
