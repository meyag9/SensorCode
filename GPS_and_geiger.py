#
#	takes GPS and geiger counter input from uart on raspberry pi and seperates it into user readable format,
#       outputs it to a text file
#
from __future__ import print_function
import release
import serial
import threading
import time
import Queue
import smbus
import sys
import time
import i2c
import release


ALT_B_RELEASE = 24384
ALT_P_RELEASE = 1000



# initialize text files that data will be written to
w = open("GPS_data.txt","a")	# 'a' - append to data log
g = open("geigerdata.txt","a")

IER = 1
FCR = 2
IIR = 2
LCR = 3
MCR = 4
LSR = 5
MSR = 6
SPR = 7
IOC = 0x0E
DLL = 0
DLH = 1
EFR = 2
RXLVL = 9


class UART(object):
	divisor_lookup = {4800:{'DLL':24, 'DLH':0}, 9600:{'DLL':12, 'DLH':0}}

	def __init__(self, i2c_address, baud_rate, initialize=True, eol=0x0A):
		self.i2c_address = i2c_address
		self.eol = chr(eol)
		self.bus = smbus.SMBus(1)
		self.buff = ""
		if initialize:
			self.setup(baud_rate)
			self.queue = Queue.Queue()
			self.thread = threading.Thread(target=self.enqueue_output, args=(self.queue,))
			self.thread.daemon = True
			self.thread.start()

	def setup(self, baud_rate):
		self.write(IER, 1)		# enable FIFO Rx interrupts
		self.write(FCR, 0x87)	# Enable Tx/Rx FIFOs, clear them, RX FIFO trigger on 56
		self.write(LCR, 3)		# 8N1
		self.write(LCR, 0x80)
		self.write(DLL, UART.divisor_lookup[baud_rate]['DLL'])
		self.write(DLH, UART.divisor_lookup[baud_rate]['DLH'])
		self.write(LCR, 3)


	def enqueue_output(self, queue):
		# run forever, looking for a line and putting it in the queue
		while True:
			line = self.build_line()		# this blocks!
			queue.put(line)


	def write(self, reg, value=None):
		reg = int(reg<<3)
		if value != None:
			self.bus.write_byte_data(self.i2c_address, reg, value)
		else:
			self.bus.write_byte(self.i2c_address, reg)
		time.sleep(0.01)


	def read(self):
		return self.bus.read_byte(self.i2c_address)


	def read_reg(self, reg):
		return self.bus.read_byte_data(self.i2c_address, reg)


	def build_line(self):
		while True:
			self.write(RXLVL)
			r = self.read()
			if r == 0:
				time.sleep(0.05)
				continue
			while r > 0:
				self.buff = self.buff + chr(self.read_reg(0))
				r -= 1
			i = self.buff.find(self.eol)
			if i >= 0:
				s = self.buff[:i].strip()
				self.buff = self.buff[i+1:]
				return s

	def get_line(self,timeout=0.01):
		try:
			line = self.queue.get(timeout=timeout)
		except Queue.Empty:
			return None
		else:
			return line


# parse_count = 0
# TEST_GPS = True
# alts = [0, 0, 0, 0, 100, 200, 1000, 2000, 5000, ALT_B_RELEASE, ALT_B_RELEASE, ALT_B_RELEASE,
# 5000, 4000, 3000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000,
# ALT_P_RELEASE, ALT_P_RELEASE, ALT_P_RELEASE,
# 900, 900, 900, 900, 900, 900, 900, 900, 900, 800, 700, 600, 500, 400, 300, 200, 100]
    	def parseGPS(self, gps_msg):
    	# if TEST_GPS:
    	# 	global parse_count, TEST_GPS, alts
    	# 	gps_alt = alts[parse_count]
    	# 	parse_count += 1
    	# 	t = parse_count
    	# 	s = "05 %d"%(t) + " $$$$$$ 000000.00 12.3456 -789.1011 deg %1.1f m\r\n"%gps_alt		#tstr + " " + gpsType + " " + time_ + " GPS not locked \n"
    	# 	print(s)
    	# 	MyGlobals.ser.write(s) #send over serial port # jhn
    	# 	MyGlobals.altitude = "%1.1f"%gps_alt
    	# 	return
            t = time.time()
    	    list1 = gps_msg.split(",") # split into list to do conversion and format
    	    try: 					#checks for corrupt data that the GPS may have sent. marked as corrupt and moves on if gps line is corrupted.
    	        gpsType = list1[0]
    		time_ = list1[1]
    		lat = dms_to_decimal(list1[2])
    		lon = dms_to_decimal(list1[4])
    		altitude = list1[9]	# global variable because commands depend on altitude
                s = "05 %d %s %d %7.4f %9.4f deg %d m"%(t,gpsType,time_,lat,lon,altitude)
            except:
    		    s = "05 {} $$$$$$ 000000.00 12.3456 -789.1011 deg 00000 m\r\n".format(t)
    	    print(s)
    	    w.write(s) #log to text file # jhn
            return s

        def parseGeiger(self, geiger_msg):
        # parse geiger data to send in certain format for telemetry
    	    list2 = geiger_msg.split(",")
    	    try:
    		t = time.time()
    		cps = list2[1]
    		cpm = list2[3]
    		usv = list2[5][1:5]
    		spd = list2[6][1:5]
                s = "04 %d %d %d %d %d uSv/hr\r\n"%(t,cps,cpm,usv,spd) # might need to pad format
    	    except:
    		s = "04 1234567890 12 345 6.78 None uSv/hr\r\n" # jhn
            print(s)
    	    g.write(s) #log data
            return s


        def dms_to_decimal(latlon):
        #converting from degrees, minutes, seconds to decimal notation
    	    deg = latlon
    	    deg = float(deg)
    	    ms = deg%100
    	    ll  = round(((deg - ms)/100 + ms/60),4)
    	    return str(ll)


        def get_alt():
             return float(altitude)


ACTUATOR_STATUS_INTERVAL = 15


def main():
	while True:
		try:
			run_main()
		except:
			pass


def run_main():
	geiger = UART(0x49, 9600)
	gps = UART(0x4d, 4800)

	last_alt = 0

	#wait for balloon release
	print("Waiting for ballon release")
	while True:
		alt = get_alt()
		if alt >= ALT_B_RELEASE:
			if last_alt >= ALT_B_RELEASE:
				break
		last_alt = alt

		gps_msg = gps.get_line()			# this is NOT blocking
		if gps_msg != None:
		   	if("$GPGGA" in gps_msg): # if GPS message, parse the string
				parseGPS(gps_msg)

		geiger_msg = geiger.get_line()		# this is NOT blocking!
		if geiger_msg != None:
			parseGeiger(geiger_msg)

		time.sleep(0.25)


	release.b_release()
	start = time.time()
	while time.time() - start <= 5:
		gps_msg = gps.get_line()			# this is NOT blocking
		if gps_msg != None:
		   	if("$GPGGA" in gps_msg): # if GPS message, parse the string
				parseGPS(gps_msg)
		geiger_msg = geiger.get_line()		# this is NOT blocking!
		if geiger_msg != None:
	    		parseGeiger(geiger_msg)
		time.sleep(0.5)


	#wait for parachute release
	print("Waiting for parachute release")
	while True:
		alt = get_alt()
		if alt <= ALT_P_RELEASE:
			if last_alt <= ALT_P_RELEASE:
				break
		last_alt = alt

		gps_msg = gps.get_line()			# this is NOT blocking
		if gps_msg != None:
		   	if("$GPGGA" in gps_msg): # if GPS message, parse the string
				parseGPS(gps_msg)

		geiger_msg = geiger.get_line()		# this is NOT blocking!
		if geiger_msg != None:
			parseGeiger(geiger_msg)

		time.sleep(0.5)


	release.p_release()
	start = time.time()
	while time.time() - start <= 5:
		gps_msg = gps.get_line()			# this is NOT blocking
		if gps_msg != None:
		   	if("$GPGGA" in gps_msg): # if GPS message, parse the string
				parseGPS(gps_msg)
		geiger_msg = geiger.get_line()		# this is NOT blocking!
		if geiger_msg != None:
	    		parseGeiger(geiger_msg)
		time.sleep(0.5)


	# until the end
	print("waiting for impact")
	while True:
		gps_msg = gps.get_line()			# this is NOT blocking
		if gps_msg != None:
		   	if("$GPGGA" in gps_msg): # if GPS message, parse the string
				parseGPS(gps_msg)

		geiger_msg = geiger.get_line()		# this is NOT blocking!
		if geiger_msg != None:
			parseGeiger(geiger_msg)

		time.sleep(0.25)
