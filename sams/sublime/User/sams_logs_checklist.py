#!/usr/bin/env python

checks = {

	#----------------------------------------------------------------------------------------------------------
	'/var/log/messages':
	[
		('Check that rarpd messages occur contiguously, once per minute.',     'rarpd_contiguous_minutely'),
		('Log tftpd connection refused to see if these match EE boot times.',  'tftpd_conn_refused_eeboots'),
		('PANIC on mb_map_full, then ask for soft reboot.',                    'mb_map_full'),
	],

	#----------------------------------------------------------------------------------------------------------
	'/var/log/sams-ii/messages':
	[
		('Check that IC system clock adjusted by no more than 2 minutes.',     'clock_adjusted_minutely'),
	],	

	#----------------------------------------------------------------------------------------------------------
	'/var/log/sams-ii/watchdoglog':
	[
		('Check for most recent ten messages.',								   'watchdog_recent_ten'),
	],	

	}

for K, L in checks.iteritems():
	print '\n', K
	for note, callable in L:
		print note, callable
