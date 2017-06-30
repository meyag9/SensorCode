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
		lat = dms_to_decimal(list1[3])
		lon = dms_to_decimal(list1[5])
		s = tstr + " " + gpsType + " " + time_ + " " + lat + " -" + lon +"\n"
	except:
		s = tstr + " " + gpsType + " " + time_ + " Corrupted Data\n"
	w.write(s)
	print (tstr, " : ", time_)

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


def dms_to_decimal(ll):		#converting from degrees, minutes, seconds to decimal notation
    if len(ll) == 8:
        degrees = ll[0]
        decimal = ll[1] + ll[2] + ll[3] + ll[4] + ll[5] + ll[6] + ll[7]
    elif len(ll) == 9:
        degrees = ll[0] + ll[1]
        decimal = ll[2] + ll[3] + ll[4] + ll[5] + ll[6] + ll[7] + ll[8]
    elif len(ll) == 10:
        degrees = ll[0] + ll[1] + ll[2]
        decimal = ll[3] + ll[4] + ll[5] + ll[6] + ll[7] + ll[8] + ll[9]
    decimal = round(((float(decimal))/60), 4)
    ll = (float(degrees))+(float(decimal))
    ll = str(ll)
    return ll

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
			if("CPS" in msg):
				parseGeiger(msg)
		if no_msg:
			time.sleep(.05)
