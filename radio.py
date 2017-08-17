from __future__ import print_function
import threading
import time
import Queue
import serial
import sys
import time

class RADIO(object):
	def __init__(self, port, baudrate, eol='\x0A'):
		self.eol = eol
		self.buff = ""
		self.ser = serial.Serial(port=port, baudrate=baudrate, bytesize=8, parity='N', stopbits=1, timeout=0, xonxoff=0, rtscts=0)
		self.ser.flushInput()
		self.ser.flushOutput()
		self.queue = Queue.Queue()
		self.thread = threading.Thread(target=self.enqueue_output, args=(self.queue,))
		self.thread.daemon = True
		self.thread.start()


	def enqueue_output(self, queue):
		# run forever, looking for a line and putting it in the queue
		while True:
			queue.put(self.build_line())		# this blocks!


	def build_line(self):
		while True:
			n = self.ser.inWaiting()
			if n == 0:
				time.sleep(0.05)
				continue
			data = self.ser.read(n)
			self.buff = self.buff + data
			i = self.buff.find(self.eol)
			if i >= 0:
				s = self.buff[:i]
				self.buff = self.buff[i+len(self.eol):]
				return s


	def get_line(self,  timeout=0.01):
		try:
			line = self.queue.get(timeout=timeout)
		except Queue.Empty:
			return None
		else:
			return line


	def write(self, data, send_eol=False):
            if send_eol:
                self.ser.write(data+self.eol)
            else:
                self.ser.write(data)

        def run_command(self, cmd): #mbg -method for implementing command
            t = time.time()
            if cmd == "bal_rel\r":
                release.b_release()
                self.write("11 %d Balloon\r\n"%t)
            elif cmd == "par_rel\r":
                self.write("11 %d Parachute\r\n"%t)
                release.p_release()
            elif cmd == "SHUT_DOWN\r":
                self.write("11 %d Pi will shutdown now\r\n"%t)
                os.system("sudo /sbin/halt")	# command to shut down the pi
            elif cmd == "take_pic\r":
                print("11 %d start picture program\r\n"%t)
                camera.capture()
            elif cmd == "act_status\r":
                self.write("11 %d Actuator Status: "%t)
                release.send_actuator_status()
            elif cmd == "close\r":
                close.close()
            elif cmd == "REBOOT\r":
                os.system("sudo /sbin/reboot")

if __name__ == "__main__":
	radio = RADIO("/dev/ttyAMA0", 9600) #changed from tty## to ttyAMA0
#	radio = RADIO("COM6", 9600, eol='@@@')

	count = 0
	while True:
		no_msg = True

		msg = radio.get_line()		# this is NOT blocking!
		if msg != None:
			no_msg = False
			tstr = time.strftime('%Y-%m-%d %H:%M:%S')
			t = time.time()
			print("%1.3f: %s" %(t, msg))
			radio.write('%d'%count)
			count += 1

		if no_msg:
			time.sleep(0.05)
