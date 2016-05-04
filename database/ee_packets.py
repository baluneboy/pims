#!/usr/bin/env python

from pims.database.pimsquery import get_ee_table_list, delete_older_ee_packets

def prune(table_list):
    for t in table_list:
        delete_older_ee_packets(t)
        
if __name__ == "__main__":
    tables = get_ee_table_list()
    prune(tables)