# MBG
# 7/7/17
# master program that calls on seperate programs that collect sensor data
#
from threading import Thread
import GPS_and_geiger
import magnetometer
from time import sleep
from c import MyGlobals

def startProgs(): #rename to 'startProgs()'
    # gps and geiger
	g = Thread(target=GPS_and_geiger.main)    # thread starts new program
    	g.daemon = True                           # Exit the server thread when the main thread terminates
	g.start()                                 #start thread execution

    # magnetometer
    	m = Thread(target=magnetometer.main)
    	m.daemon = True
    	m.start()

    # pressure sensor
#    	p = Thread(target=pressure.main)
#    	p.daemon = True
#    	p.start()

    # accelerometer
#    	a = Thread(target=accel.main)
#    	a.daemon = True
#    	a.start()



    	return
#    	while(True): # Normal test would be until resource allocation time is up
#        sleep(1)

def command(cmd):
    	if cmd == "c":
        	print("You are in command mode: ")    # in command mode, suspend threads
        	MyGlobals.stop_threads = True
        	print("%i"%MyGlobals.stop_threads)  # just for testing , checking status of thread
 		while True:
        		cmd = raw_input(">>")
                	if cmd == "B_REL": #if command detected, trigger manual balloon release
                		print("Balloon will now be released")
                		#r = Thread(target=balloon_release.man_b_release)
               			#r.daemon = True
                		#r.start()
        		if cmd == "start":
                		MyGlobals.stop_threads = False #continue with threads data
                    		#startProgs()


if __name__ == "__main__":
	startProgs() # send threads to start each sensor program

	while True:         #listen for a command ( listen through the radio )
        	cmd = MyGlobals.ser.readline()
	    	if cmd != None:
            		command(cmd)
		    	break
