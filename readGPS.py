from __future__ import print_function
import threading
import time
import Queue
import sys
import time

w = open("data.txt","w")

def parseGPS(gps_msg):
	tstr = time.strftime('%Y-%m-%d %H:%M:%S')
	t = time.time()
	list1 = gps_msg.split(",")
	gpsType = list1[0]
	time_ = (list1[1])
	s = tstr + " " + gpsType + " " + time_ + "\n"
	w.write(s)
	print (tstr, " : ", time_)


if __name__ == "__main__":
	f = open(sys.argv[1], "rb")

	while True:
		no_msg = True
		msg = f.readline()

		if msg == "":
			break
		if msg != None:
			no_msg = False
			if("$GPRMC" in msg):
				parseGPS(msg)


		if no_msg:
			time.sleep(.05)
