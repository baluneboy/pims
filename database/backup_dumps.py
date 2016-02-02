#!/usr/bin/env python

import os
import sys
import traceback
import subprocess
import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
from samsquery import _UNAME_SAMS, _PASSWD_SAMS
from pims.files.utils import mkdir_p
from pims.database.backup_dumps_info import TABLE_INFO_DEFAULT

# input parameters
defaults = {
'host':     'yoda',
'start':    '2014-12-01',
'stop':     '2015-02-01',
'dryrun':   'False',        # False for default processing; True to run show_count
}
parameters = defaults.copy()


# perhaps some useful dates
_THREE_MONTHS_AGO = datetime.date.today() + relativedelta(months=-3)
_SIX_MONTHS_AGO = datetime.date.today() + relativedelta(months=-6)
_NINE_MONTHS_AGO = datetime.date.today() + relativedelta(months=-9)


class WhereClauseForCmdLine(object):
    
    def __init__(self, time_field, start=_SIX_MONTHS_AGO, stop=_THREE_MONTHS_AGO):
        self.time_field = time_field
        self.start = start
        self.stop = stop

    def __str__(self):
        s = "%s >= '%s' and %s < '%s'" % (self.time_field, self.start, self.time_field, self.stop)
        return "--where " + '"' + s + '"'


class WhereClause(WhereClauseForCmdLine):

    def __str__(self):
        s = "where %s >= '%s' and %s < '%s'" % (self.time_field, self.start, self.time_field, self.stop)
        return s
    
    
class DumpSuffix(object):

    def __init__(self, schema, table, start=_SIX_MONTHS_AGO, stop=_THREE_MONTHS_AGO):
        self.schema = schema
        self.table = table
        self.start = start
        self.stop = stop
        time_field, action = TABLE_INFO_DEFAULT[ (self.schema, self.table) ]
        self.time_field = time_field
        self.where_clause = WhereClauseForCmdLine(self.time_field, start=self.start, stop=self.stop)
        
    def __str__(self):
        return '%s %s %s' % (self.where_clause, self.schema, self.table)    


class MysqlDumpCommand(object):
    
    def __init__(self, host, schema, table, action,
                 start=_SIX_MONTHS_AGO, stop=_THREE_MONTHS_AGO,
                 backup_dir='/misc/yoda/backup/mysql/gzips',
                 uname=_UNAME_SAMS, pword=_PASSWD_SAMS):
        self.host = host
        self.schema = schema
        self.table = table
        self.action = action
        self.start = start
        self.stop = stop
        self.backup_dir = backup_dir
        self.uname = uname
        self.pword = pword
        self.dump_suffix = self.get_dump_suffix()
        self.suffix = str( self.dump_suffix )
        self.time_field = self.dump_suffix.time_field
        self.backup_filename = self.get_backup_filename()
        self.dump_command = self.get_dump_command()
        self.count_command = self.get_count_command()

    def __str__(self):
        s = 'mysqldump from host=%s to file=%s' % (
            self.host, self.backup_filename )
        return s
    
    def show_count(self):
        c = int( self.run_count_command() )
        return 'COUNT : %9d records from %s.%s where %s >= "%s" and %s < "%s"' % (
            c, self.schema, self.table, self.time_field, self.start, self.time_field, self.stop )

    def do_backup(self):
        results = self.run_dump_command()
        return 'BACKUP: ran %s' % str(self)
        
    def get_backup_filename(self):
        sub_dir = '%d' % self.start.year
        the_dir = os.path.join(self.backup_dir, sub_dir)
        mkdir_p(the_dir)
        name = '%s_to_%s_%s_%s.sql.gz' % (self.start, self.stop, self.schema, self.table)
        return os.path.join(the_dir, name)
        
    def get_dump_suffix(self):
        return DumpSuffix(self.schema, self.table, self.start, self.stop)

    def get_count_command(self):
        # mysql -h yoda -u UNAME -pHUGPWORD samsnew -e "select count(*) from gse_packet;" --batch -N
        where_clause = WhereClause(self.time_field, self.start, self.stop)
        cmd = 'mysql -h %s -u %s -p%s %s -e "select count(*) from %s %s;" --batch -N' % (
            self.host, self.uname, self.pword, self.schema, self.table, where_clause )
        return cmd

    def run_count_command(self):
        p = subprocess.Popen([self.count_command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        results, err = p.communicate()
        return results
    
    def get_dump_command(self):
        tstamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
        cmd = 'mysqldump --user=%s --password=%s --host=%s %s | gzip > %s' % (
            self.uname, self.pword, self.host, self.suffix, self.backup_filename )
        return cmd

    def run_dump_command(self):
        p = subprocess.Popen([self.dump_command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        results, err = p.communicate()
        return results


def parametersOK():
    """check for reasonableness of parameters entered on command line"""    
    
    # convert start & stop parameters to date objects
    parameters['start'] = parser.parse( parameters['start'] ).date()
    parameters['stop'] = parser.parse( parameters['stop'] ).date()
    
    # map from (schema, table) to table info & default action
    try:
        parameters['dryrun'] = eval(parameters['dryrun'])
        assert( isinstance(parameters['dryrun'], bool))
    except Exception, err:
        print 'cound not handle dryrun parameter, was expecting it to eval to True or False'
        #print traceback.format_exc() # or print sys.exc_info()[0]
        return False    
        
    return True


def printUsage():
    """print short description of how to run the program"""
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and DEFAULT values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])


def backup_tables(host, start, stop):
    """explain this where the real work is done"""
    
    # decide if we do dry run or actually run with defaults
    if parameters['dryrun']:
        from pims.database.backup_dumps_info import TABLE_INFO_DRYRUN as TABLE_INFO
    else:
        from pims.database.backup_dumps_info import TABLE_INFO_DEFAULT as TABLE_INFO
    
    # iterate over table info dictionary
    for st, ta in TABLE_INFO.iteritems():
        schema, table  = st[0], st[1]
        tfield, action = ta[0], ta[1]
        mdc = MysqlDumpCommand(host, schema, table, action, start=start, stop=stop)
        #print mdc
        result = getattr(mdc, action)() # call method referenced by action
        print result


def main(argv):
    """describe what this routine does here"""
    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parametersOK():
            #print parameters
            try:
                backup_tables(parameters['host'], parameters['start'], parameters['stop'])
            except Exception, err:
                print 'parameters', parameters
                print traceback.format_exc() # or print sys.exc_info()[0]
                return -1
            
            return 0

    printUsage()  


if __name__ == '__main__':
    sys.exit(main(sys.argv))
    