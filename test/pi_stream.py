from motor import Motor
from RPi import GPIO
import time, sys, termios, tty
import struct
import io
import socket
import picamera

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

class StreamDrive(object):

    def __init__(self):
        # Set up GPIO for RPi
        GPIO.setmode(GPIO.BOARD)
        forwardPin = 7
        backwardPin = 11
        leftPin = 13
        rightPin = 15
        controlStraightPin = 29
        self.motor = Motor(forwardPin, backwardPin, controlStraightPin, leftPin, rightPin)
        self.sensor = UltrasonicSensor()
        # Initialize server for receiving driving instructions
        self.server_socket = socket.socket()
        self.server_socket.bind(('0.0.0.0', 8000))
        self.server_socket.listen(0)
        self.server_connection, self.client_address = self.server_socket.accept()
        print("Connection from: ", self.client_address)
        # Initialize client for streaming camera pictures
        self.client_socket = socket.socket()
        self.client_socket.connect(('192.168.1.11', 8000))
        # Make a file-like object out of the client connection
        self.client_connection = self.client_socket.makefile('wb')
        # Start the stream
        self.stream()

    def stream(self):
        try:
            # Initialize camera and allow some warmup time, create stream
            self.camera = picamera.PiCamera()
            self.camera.resolution = (320, 240)
            self.camera.framerate = 10
            time.sleep(2)
            start = time.time()
            stream = io.BytesIO()
            for frame in self.camera.capture_continuous(stream, 'jpeg',
                                                        use_video_port = True):
                # Write the length of the capture to the stream
                # and flush to make sure it gets sent
                self.client_connection.write(struct.pack('<L', stream.tell()))
                self.client_connection.flush()
                # Rewind the stream and send image data through
                stream.seek(0)
                self.client_connection.write(stream.read())
                # Reset stream for next capture
                stream.seek(0)
                stream.truncate()
                # Write sensor data to server
                distance = self.sensor.measure_average()
                self.server_connection.send(struct.pack("f", distance))
                # Get the pressed key
                key = self.server_connection.recv(1024).decode()
                if (key == "w"):
                    self.motor.forward()
                elif (key == "s"):
                    self.motor.backward()
                elif (key == "a"):
                    self.motor.forward_left()
                elif (key == "d"): 
                    self.motor.forward_right()
                elif (key == "space"):
                    self.motor.stop()
                elif (key == "x"):
                    print("Program terminated")
                    break
                else:
                    self.motor.stop()
                key = ""
            # Write a length of 0 to the stream to signal we're done
            self.client_connection.write(struct.pack('<L', 0))

        finally:
            self.client_connection.close()
            self.client_socket.close()
            self.server_connection.close()
            self.server_socket.close()
            GPIO.cleanup()

if __name__ == '__main__':
    StreamDrive()






