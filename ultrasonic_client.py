import RPi.GPIO as GPIO
import time
import socket
import struct

# Create a socket and bind to host
client_socket = socket.socket()
client_socket.connect(('192.168.1.15', 8002))

def measure():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    start = time.time()
    stop = time.time()
 
    # save start time
    while GPIO.input(GPIO_ECHO) == 0:
        start = time.time()
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        stop = time.time()
 
    # time difference between start and arrival
    time_elapsed = stop - start
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (time_elapsed * 34300) / 2
 
    return distance

def measure_average():
    # Record the distance at three times and average the results
    distance1 = measure()
    time.sleep(0.1)
    distance2 = measure()
    time.sleep(0.1)
    distance3 = measure()
    average = (distance1 + distance2 + distance3) / 3
    
    return average

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BOARD)
 
#set GPIO Pins
GPIO_TRIGGER = 16
GPIO_ECHO = 18
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

try:
    while True:
        distance = measure_average()
        print('Distance: %.1f' % distance)
        client_socket.send(struct.pack("f", distance))
        time.sleep(0.5)
finally:
    client_socket.close()
    GPIO.cleanup()


