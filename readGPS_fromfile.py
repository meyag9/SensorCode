#
#	reads gps and geiger value only from a given text file and seperates it into a user readable format 
#

from __future__ import print_function
import threading
import time
import Queue
import sys
import time

# ***exception handling can be refined***

w = open("gpsdata.txt","w")
g = open("geigerdata.txt","w")

def parseGPS(gps_msg):
	tstr = time.strftime('%Y-%m-%d %H:%M:%S')
	t = time.time()
	list1 = gps_msg.split(",")
	try:					#checks for corrupt data that the GPS may have sent. marked as corrupt and moves on if gps line is corrupted.
		gpsType = list1[0]
		time_ = (list1[1])
		lat = dms_to_decimal(list1[2])
		lon = dms_to_decimal(list1[4])
		s = tstr + " " + gpsType + " " + time_ + " " + lat + " -" + lon +"\n"
	except:
		s = tstr + " " + gpsType + " " + time_ + " Corrupted Data\n"
	w.write(s)
	#print (tstr, " : ", time_)

def parseGeiger(geiger_msg):
	tstr = time.strftime('%Y-%m-%d %H:%M:%S')
	list2 = geiger_msg.split(",")
	try:
		cps = list2[0] + ":"+ list2[1]
		cpm = list2[2] + ":"+ list2[3]
		usv = list2[4] + ":"+ list2[5]
		s = cps + "" + cpm + "" + usv + "\n"
	except:
		s = tstr + " " + " Corrupted Data\n"
	g.write(s)


def dms_to_decimal(latlon):		#converting from degrees, minutes, seconds to decimal notation
	deg = latlon
	deg = float(deg)
	ms = deg%100
	ll  = (deg - ms)/100 + ms/60
	return str(ll)


if __name__ == "__main__":
	f = open(sys.argv[1], "rb")

	while True:
		no_msg = True
		msg = f.readline()

		if msg == "":
			break
		if msg != None:
			no_msg = False
			if("$GPGGA" in msg): # only accept GPRMC format
				parseGPS(msg)
			if("CPS" in msg): # Geiger counter data
				parseGeiger(msg)
		if no_msg:
			time.sleep(.05)
