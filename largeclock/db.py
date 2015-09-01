from MySQLdb import *

def query_aos(passwd):
    con = Connection(host='yoda', user='samsops', passwd=passwd, db='samsnew')
    cursor = con.cursor()
    cursor.execute('select ku_timestamp, ku_aos_los_status from gse_packet_rt;')
    results = cursor.fetchall();
    cursor.close()
    con.close()
    ku_timestamp, ku_aos_los = results[0]
    return ku_timestamp, ku_aos_los


