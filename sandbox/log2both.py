#!/usr/bin/env python

import logging

logFormatter = logging.Formatter("%(asctime)s %(threadName)s %(levelname)s %(message)s")

log = logging.getLogger('pims.sandbox.log2both')
log.setLevel(logging.INFO)

fileHandler = logging.FileHandler("{0}/{1}.log".format('/tmp', 'fileName'))
fileHandler.setFormatter(logFormatter)
log.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
log.addHandler(consoleHandler)

log.debug('debug')
log.info('info')
log.warning('warning')
log.error('error')
log.critical('critical')