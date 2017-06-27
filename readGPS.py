from __future__ import print_function
import threading
import time
import Queue
import sys
import time
from pyproj import Proj


def parseGPS(gps_msg):
	if("$GPRMC" in gps_msg):
		return gps_msg


if __name__ == "__main__":

	f = open(sys.argv[1], "rb")
	w = open("data.txt","w")

	while True:
		no_msg = True

		#gps_msg = gps.get_line()		# this is NOT blocking!
		gps_msg = f.readline()
		if gps_msg == "":
			break
		if gps_msg != None:
			no_msg = False
			tstr = time.strftime('%Y-%m-%d %H:%M:%S')
			t = time.time()
			msg = parseGPS(gps_msg)
			if msg != None:
				list1 = msg.split(",")
				gpsType = list1[0]
				time_ = list1[1]
				lat = list1[3] + list1[4]
				lon = list1[5] + list1[6]
				msgstr = tstr + " " + gpsType + " "+ lat + " " + lon
				w.write(msgstr+"\n")
				print (tstr, " : ", time_)

		if no_msg:
			time.sleep(.05)
