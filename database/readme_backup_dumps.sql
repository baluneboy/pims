# CHANGE DATE FIRST TO KEEP MOST RECENT 4 MONTHS, then do this:
# mysql -u root -h yoda -p samsnew < readme_backup_dumps.sql

delete from samsnew.command_receipt_log where Timestamp < '2016-05-01';
delete from samsnew.cu_packet where timestamp < '2016-05-01';
delete from samsnew.ICU_messages where date < '2016-05-01';
delete from samsnew.gse_packet where ku_timestamp < '2016-05-01';
delete from samsnew.tshes_house_packet where timestamp < '2016-05-01';
delete from samsnew.tshes_accel_packet where timestamp < '2016-05-01';
delete from samsnew.ee_packet where timestamp < '2016-05-01';
delete from samsnew.se_accel_packet where timestamp < '2016-05-01';
