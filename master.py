# MBG
# 7/7/17
# master program that calls on seperate programs that collect sensor data
#
from threading import Thread
import GPS_and_geiger
import magnetometer
from time import sleep

def main():
    # Create thread to call on separate program
    g = Thread(target=GPS_and_geiger.main)
    # Exit the server thread when the main thread terminates
    g.daemon = True
    #start thread execution
    g.start()

    m = Thread(target=magnetometer.main)
    m.daemon = True
    m.start()


    while(True): # Normal test would be until resource allocation time is up
        sleep(1)


if __name__ == "__main__":
    main()
