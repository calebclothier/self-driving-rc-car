import RPi.GPIO as GPIO
import time
import socket
import struct

class UltrasonicSensor(object):

    def __init__(self):
        #GPIO Mode (BOARD / BCM)
        GPIO.setmode(GPIO.BOARD)
        #set GPIO Pins
        self.GPIO_TRIGGER = 16
        self.GPIO_ECHO = 18
        #set GPIO direction (IN / OUT)
        GPIO.setup(self.GPIO_TRIGGER, GPIO.OUT)
        GPIO.setup(self.GPIO_ECHO, GPIO.IN)
        
    def measure(self):
        # Set Trigger to HIGH
        GPIO.output(self.GPIO_TRIGGER, True)
        # Set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(self.GPIO_TRIGGER, False)
        # Initialize start and stop times
        start = time.time()
        stop = time.time()
        # Save start time
        while GPIO.input(self.GPIO_ECHO) == 0:
            start = time.time()
        # Save time of arrival
        while GPIO.input(self.GPIO_ECHO) == 1:
            stop = time.time()
        # Time difference between start and arrival
        time_elapsed = stop - start
        # Multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (time_elapsed * 34300) / 2
        return distance

    def measure_average(self):
        # Record the distance at three times and average the results
        distance1 = self.measure()
        time.sleep(0.1)
        distance2 = self.measure()
        time.sleep(0.1)
        distance3 = self.measure()
        average = (distance1 + distance2 + distance3) / 3
        return average

class UltrasonicClient(object):

    def __init__(self):
        # Create a socket and bind to host
        self.client_socket = socket.socket()
        self.client_socket.connect(('192.168.1.11', 8002))
        self.sensor = UltrasonicSensor()
        self.stream()

    def stream(self)
        # Send distance data to server on another computer
        try:
            while True:
                # Write sensor data to server
                distance = self.sensor.measure_average()
                print('Distance: %.1f' % distance)
                self.client_socket.sendall(struct.pack("f", distance))
                time.sleep(0.5)
        finally:
            self.client_socket.close()
            GPIO.cleanup()

if __name__ == '__main__':
    UltrasonicClient()




