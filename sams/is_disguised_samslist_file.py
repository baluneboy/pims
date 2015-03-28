import os
import re
import subprocess

MAXFILESIZE = 50000
SAMSLIST_CMDS = [
    "ps -ef",
    "df -k",
    "ls -al /usr/tgz",
    ]

def grep_cmd(cmdstr, fname):
    p = subprocess.Popen('grep "^%s" %s' % (cmdstr, fname), shell=True, stdout=subprocess.PIPE)
    output, _ = p.communicate()
    if len(output) > 0:
        return True
    else:
        return False

def is_disguised_samslist_file(file_name):

    fsize = os.path.getsize(file_name)
    path = os.path.dirname(file_name)
    base_name = os.path.basename(file_name).lower()
    name, extension = os.path.splitext(base_name)

    # check for txt or asc extension
    if extension not in ['.txt', '.asc']:
        print '%s does not have proper extension for disguised samslist checking' % file_name
        return False

    # check for max bytes file size
    if fsize > MAXFILESIZE:
        print '%s too big to be a disguised samslist text file' % file_name        
        return False

    # final test if we can grep to match all SAMSLIST_CMDS
    has_cmd = map(lambda c: grep_cmd(c, file_name), SAMSLIST_CMDS)
    has_all_cmds = all(has_cmd)
    if not has_all_cmds:
        print '%s does not appear to have all samslist cmds for disguised samslist checking' % file_name
    return has_all_cmds
