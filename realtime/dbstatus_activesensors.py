#!/usr/bin/env python
# $Id $

from string import *
import struct
import sys
from MySQLdb import *
from time import *
from commands import *
from accelPacket import guessPacket
from pims.database.pimsquery import db_connect

# table names (i.e. sensors) to ignore that would otherwise get displayed note
# that these might not have sensor sample rate or location, so it's not an
# active sensor
_IGNORE = [ '121f08badtime', '121f08goodtime', 'Abias',
			'Abiasavg', 'Bbias', 'Bbiasavg', 'besttmf', 'Cbias', 'Cbiasavg',
			'cmg', 'finalbias_combine', 'gse', 'hirap_bogus', 'housek',
			'mcor_121f03', 'mcor_hirap', 'mcor_oss', 'pbesttmf', 'poss',
			'powerup', 'radgse', 'sec_hirap', 'sec_oss',
			'soss', 'soss', 'textm', 'emptytable' ] 

# convert "Unix time" to "Human readable" time
def UnixToHumanTime(utime):
	fraction = utime - int(utime)
	s = split(getoutput('date -u -d "1970-01-01 %d sec" +"%%Y %%m %%d %%H %%M %%S"' % int(utime)) )
	s[5] = atoi(s[5]) + fraction
	return "%s-%s-%s %s:%s:%06.4f" % tuple(s)

# create dict of distinct coord_name (i.e. sensor) entries from pad.coord_system_db on kyle
def get_locations():
	locations = {}
	results = db_connect('select distinct(coord_name) from pad.coord_system_db', 'kyle')
	for r in results:
		locs = db_connect('select location_name from pad.coord_system_db where coord_name = "%s" order by time desc limit 1' % r[0], 'kyle')
		locations[ r[0]] = locs[0][0]
	return locations

def get_samplerate(p):
	# guess packet and print details parsed from the packet blob
	pkt = guessPacket(p)
	if pkt.type == 'unknown':
		return None
	else:
		return pkt.rate()

if __name__ == '__main__':
	pimsComputers = ['chef', 'ike', 'butters', 'kyle', 'cartman', 'stan', 'kenny', 'timmeh', 'tweek', 'mr-hankey', 'manbearpig', 'towelie']
	myname = split(getoutput('uname -a'))[1]
	myname = split(myname, '.')[0]

	# first check to see if the computer is up
	up = {}
	for c in pimsComputers:
		result = getoutput("dbup.py %s" % c)
		if result == 'NO':
			up[c]=0
			print '%9s is DOWN' % c
		else:
			up[c]=1

	# get locations (if kyle's up)
	locs = get_locations() if up['kyle'] else None

	timeNow = time()
	print ' time now: ', UnixToHumanTime(timeNow)
	print '%11s %12s %8s %19s %19s %10s' % ('COMPUTER', '_____________TABLE', '___COUNT', '___________MIN-TIME', '___________MAX-TIME', '________AGE'),
	print '%8s %s' % ('____RATE', 'LOCATION')

	# iterate over computers
	for c in pimsComputers:
		if up[c]:
			n = c
			if c == myname:
				n = 'localhost' # mysql permissions require localhost if you are local
			
			# iterate over tables (i.e. sensors) on this computer
			results = db_connect('show tables', n)
			
			# flatten nested tuple (results) using list comprehension
			table_list = [element for tupl in results for element in tupl]
			sensors = list( set(table_list) - set(_IGNORE) )
			
			for sensor in sensors:
				r = db_connect('show columns from %s' % sensor, n)
				timeFound = 0
				for col in r:
					if col[0] == 'time':
						timeFound = 1
						break

				if timeFound:
					r = db_connect('select count(time) from %s' % sensor, n)
					count = r[0][0]
					if count == 0:
						minTime = 0
						maxTime = 0
						age = time() # time now
					else:
						# get three values in one pass in case slow database is not indexed
						r = db_connect('select max(time), from_unixtime(min(time)), from_unixtime(max(time)) from %s' % sensor, n)
						maxTimeF = r[0][0]
						minTime = r[0][1]
						maxTime = r[0][2]
						age = time() - maxTimeF
						rp = db_connect('select time, packet from %s order by time desc limit 1' % sensor, n)
						packet = rp[0][1]

					# get location info
					if locs:
						loc = locs[sensor] if sensor in locs else 'None'
					else:
						loc = 'kyle down'
					
					# get sample rate from packet blob
					rate = '%.1f' % get_samplerate(packet)
					
					# output text
					print '%11s %18s %8d %19s %19s %11d %8s %s' % (c, sensor, count, minTime, maxTime, age, rate, loc)
