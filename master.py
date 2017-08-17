# Author: Meya Gorbea
# 7/7/17
# program to recieve data from multiple sensors
# TODO: Restructure and take in commands for actuators

from threading import Thread
import time
import GPS_and_geiger
import magnetometer
#import release
#import bppv_volts
#import serial
import os
import radio
import accel
#import pressure
#import close
import cpu_temp
#import actuators


def send():
    radio.write(s)


def main():
    r = radio.RADIO("/dev/ttyAMA0", 9600) #changed from tty## to ttyAMA0
    geiger = GPS_and_geiger.UART(0x49, 9600)
    gps = GPS_and_geiger.UART(0x4d, 4800)
    acc = accel.ACCELEROMETER(12, 25)
    mag = magnetometer.MAG3110(0x0E)
    #press =  pressure.PRESSURE(0x48)

    
    # get a Radio object
    # make method of Radio object for Sending
    # For receive, use get_line() (return: None, or a string)

    id = mag.get_id()
    print("ID = %02X"%id)
    (x, y, z) = mag.get_offsets()
    print("Offsets: x=%04X, y=%04X, z=%04X" %(x, y, z))

    mag.start_readings()
    while True:
        # magnetometer 
        t = time.time()
        data = mag.get_readings()
        if data != None:
            mag.log(data)
            

        # listen for command through the radio
        cmd = r.get_line()
        if cmd != None:
            r.run_command(cmd)

        # accel
	data = acc.get_acceleration()
	if data != None:
            acc.log(data) # print and write to file 

        # gps 
        gps_msg = gps.get_line()			# this is NOT blocking
	if gps_msg != None:
	    if("$GPGGA" in gps_msg): # if GPS message, parse the string
                s = gps.parseGPS(gps_msg) # log in the function, transmit here
                #radio.write(s)

                
        # geiger 
        geiger_msg = geiger.get_line()		        # this is NOT blocking!
        if geiger_msg != None:
	    s = geiger.parseGeiger(geiger_msg)
            #radio.write(s)

	# pressure
##	pressure = press.get_pressure()
##      if pressure != None:
##          print pressure # also log and trasmit

        # battery/therm temp
        temps = cpu_temp.get_temps() # log it
        # radio.write(temps)

if __name__ == "__main__":  # read from radio is not working
    main()
