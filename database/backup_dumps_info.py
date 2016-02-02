#!/usr/bin/env python

# a dictionary that maps (schema, table) to table info & default action
# NOTE: the DEFAULT_ACTION tuple element MUST correspond to a method of
#      the MysqlDumpCommand class in backup_dumps module
TABLE_INFO_DEFAULT = {
    # SCHEMA    TABLE                   TIME_FIELD          DEFAULT_ACTION
    #---------------------------------------------------------------------
    ('samsnew', 'ICU_messages'):        ('date',            'do_backup'),
    ('samsnew', 'command_receipt_log'): ('Timestamp',       'do_backup'),
    ('samsnew', 'cu_packet'):           ('timestamp',       'do_backup'),
    ('samsnew', 'ee_packet'):           ('timestamp',       'do_backup'),
    ('samsnew', 'gse_packet'):          ('ku_timestamp',    'do_backup'),
    ('samsnew', 'tshes_house_packet'):  ('timestamp',       'do_backup'),
    #-----------------------------------------------------------------------     
    ('samsnew', 'se_accel_packet'):     ('timestamp',       'show_count'), # ACTUALLY JUST WANT TO PRUNE, NO BACKUP DUMP
    ('samsnew', 'tshes_accel_packet'):  ('timestamp',       'show_count'), # ACTUALLY JUST WANT TO PRUNE, NO BACKUP DUMP
    #=======================================================================
    ('samsmon', 'cu_packet'):           ('timestamp',       'show_count'),
    ('samsmon', 'ee_packet'):           ('timestamp',       'show_count'),
    ('samsmon', 'gse_packet'):          ('ku_timestamp',    'show_count'),
    ('samsmon', 'se_accel_packet'):     ('timestamp',       'show_count'),
    }


# for dry run, same table as above EXCEPT change all actions to show_count
TABLE_INFO_DRYRUN = dict()
for schema_table, tfield_action in TABLE_INFO_DEFAULT.iteritems():
    TABLE_INFO_DRYRUN[schema_table] = (tfield_action[0], 'show_count')

#print TABLE_INFO_DRYRUN
#print '-------\n'
#print TABLE_INFO_DEFAULT