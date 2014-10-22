#!/usr/bin/python2
# -*- coding: utf-8 -*-
# vim: set ts=4 noet: 
#
# Copyright (C) 2014  Alexander Sosna <Alexander.Sosna@credativ.de>
# License: http://www.gnu.org/licenses/gpl.html GPL version 2 or higher
# Version: 0.1
#
# usage: ./check_traffic.py 
# Gives performance data for network traffic on all interfaces
# No limit is checked
#
import time

# settings
DEBUG = False
procfile = "/proc/net/dev"
sleeptime = 5
unit= 'kbit/s' 

# available units
units = {	'bit/s': 1,
			'Byte/s': 8,
			'kbit/s': 1024,
			'kByte/s/s': 1024*8,
			'Mbit/s': 1024*1024,
			'MByte/s': 1024*1024*8,
			'Gbit/s': 1024*1024*1024,
			'GByte/s': 1024*1024*1024*8
		}

# Icinga return codes
OK = 0;
WARNING = 1;
CRITICAL = 2;

# use desired unit
def calc_unit(i):
	return (i / units[unit] / sleeptime)

# get device data from proc
def get_devices(procfile):
	devices = []
	with open(procfile) as proc:
		for device in proc:
			if device.find(':') != -1:
				d = device.strip().split()
				new_dev = {	'if':		d[0].split(':')[0],
							'rxbyte':	long(d[1]),
							'rxpacket':	long(d[2]),
							'rxerror': 	long(d[3]),
							'rxdrop':	long(d[4]),
							'rxfifo':	long(d[5]),
							'rxframe':	long(d[6]),
							'rxcompr':	long(d[7]),
							'rxmulti':	long(d[8]),
							'txbyte':	long(d[9]),
							'txpacket':	long(d[10]),
							'txerror': 	long(d[11]),
							'txdrop':	long(d[12]),
							'txfifo':	long(d[13]),
							'txcolls':	long(d[14]),
							'txcarrier':long(d[15]),
							'txcompr':	long(d[16])
						}
				devices.append(new_dev);
	return devices

def icinga_output(data):
	count = 0
	perf = ''
	for dev in data:
		count+= 1
		#perf += "rxrate-"+dev['if']+"="
		#perf += dev['rxrate']+";"+dev['txrate']+";; "
		perf += dev['if']+"-rx-"+unit+"="+str(dev['rx'])+", ";
		perf += dev['if']+"-tx-"+unit+"="+str(dev['tx'])+", ";
	return "TRAFFIC OK - NO LIMIT SET - " + str(count) + " interfaces checked | " + perf

# main
old_devs = get_devices(procfile)
time.sleep(sleeptime)
new_devs = get_devices(procfile)

count = 0
div = []
for new_dev in new_devs:
	for old_dev in old_devs:
		if new_dev['if'] == old_dev['if']:
			new_div = {	'if': new_dev['if'],
						'rx': calc_unit(new_dev['rxbyte'] - old_dev['rxbyte']),
						'tx': calc_unit(new_dev['txbyte'] - old_dev['txbyte'])
						}
			div.append(new_div)
			break

print icinga_output(div)
exit(OK)
