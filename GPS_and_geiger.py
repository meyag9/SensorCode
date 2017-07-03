from __future__ import print_function
import threading
import time
import Queue
import smbus
import sys
import time
import i2c

# initialize text files that I will write data to
w = open("gpsdata.txt","w")
g = open("geigerdata.txt","w")

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


def parseGPS(gps_msg):
	tstr = time.strftime('%Y-%m-%d %H:%M:%S')
	t = time.time()
	list1 = gps_msg.split(",") # split into list to do conversion and format
	try: 					#checks for corrupt data that the GPS may have sent. marked as corrupt and moves on if gps line is corrupted.
		gpsType = list1[0]
	    	time_ = (list1[1])
	    	lat = dms_to_decimal(list1[2])
	    	lon = dms_to_decimal(list1[4])
	    	s = tstr + " " + gpsType + " " + time_ + " " + lat + " -" + lon +"\n"
		print(s)
	except:
	    	s = tstr + " " + gpsType + " " + time_ + " Corrupted Data\n"
	print(s)
	w.write(s)



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
	if s == "":
		s = "No data collected"
	g.write(s)



def dms_to_decimal(latlon):		#converting from degrees, minutes, seconds to decimal notation
	deg = latlon
	deg = float(deg)
	ms = deg%100
	ll  = (deg - ms)/100 + ms/60
	return str(ll)

if __name__ == "__main__":
	geiger = UART(0x49, 9600)
	gps = UART(0x4d, 4800)

	while True:
		no_msg = True

		geiger_msg = geiger.get_line()		# this is NOT blocking!
		if geiger_msg != None:
			no_msg = False
	       		parseGeiger(geiger_msg)


		gps_msg = gps.get_line()		# this is NOT blocking
	    	if gps_msg != None:
			no_msg = False
	            	if("$GPGGA" in gps_msg): # if GPS message, parse the string
				parseGPS(gps_msg)

		if no_msg:  #if no message in queue, wait until there is
			print(".", end="")
			sys.stdout.flush()
		time.sleep(.1)
