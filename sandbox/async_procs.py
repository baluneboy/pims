#!/usr/bin/env python

import time
from subprocess import Popen, PIPE

p = Popen(['ls -alrth /tmp/two'], stdout=PIPE, stderr=PIPE, shell=False)
retcode = p.poll()
print retcode
p.terminate()

# def handle_results(outstr):
# 	print outstr


# running_procs = []
# for pth in ['one', 'two', 'nine']:
# 	running_procs.append( Popen(['/home/pims/dev/programs/bash/async_test.bash', '-i /tmp/%s' % pth, '-s 4'], stdout=PIPE, stderr=PIPE) )

# while running_procs:
# 	for proc in running_procs:
# 		retcode = proc.poll()
# 		if retcode is not None:  # process finished
# 			running_procs.remove(proc)
# 			break
# 		else:  # no process is done yet, wait a bit and check again
# 			time.sleep(0.1)
# 			continue

# 	# a process has finished with retcode
# 	if retcode != 0:
# 		print retcode, 'error handling goes here'

# 	handle_results(proc.stdout)
