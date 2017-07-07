# MBG
# 7/7/17
# master program that calls on seperate programs that collect sensor data
#
from threading import Thread
import GPS_and_geiger
import mag_test
from time import sleep

def main():
    # Create thread to call on separate program
    GPS = Thread(target=GPS_and_geiger.main)
    # Exit the server thread when the main thread terminates
    GPS.daemon = True
    #start thread execution
    GPS.start()

    mag = Thread(target=magnetometer.main)
    mag.daemon = True
    mag.start()


    while(True): # Normal test would be until resource allocation time is up
        sleep(1)


if __name__ == "__main__":
    main()
