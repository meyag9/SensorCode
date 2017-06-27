from __future__ import print_function
import threading
import time
import Queue
import sys
import time


def parseGPS(gps_msg):
	if("$GPRMC" in gps_msg):
		return gps_msg

#def convertLat():


if __name__ == "__main__":

	f = open(sys.argv[1], "rb")

	while True:
		no_msg = True
		#list1 = []

		#gps_msg = gps.get_line()		# this is NOT blocking!
		gps_msg = f.readline()
		if gps_msg == "":
			break
		if gps_msg != None:
			no_msg = False
			tstr = time.strftime('%Y-%m-%d %H:%M:%S')
		#print(tstr)
			t = time.time()
			msg = parseGPS(gps_msg)
			if msg != None:
				list1 = msg.split(",")
				gpsType = list1[0]
				time_ = (list1[1])
				print (tstr, " : ", time_)
		#	time.sleep(1)

		if no_msg:
			time.sleep(.05)
