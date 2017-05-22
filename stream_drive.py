from motor import Motor
from RPi import GPIO
import time, sys, termios, tty
import struct
import io
import socket
import picamera

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
        # Initialize server for receiving driving instructions
        self.server_socket = socket.socket()
        self.server_socket.bind(('0.0.0.0', 8000))
        self.server_socket.listen(0)
        self.server_connection = self.server_socket.accept()[0]
        # Initialize client for streaming camera pictures
        self.client_socket = socket.socket()
        self.client_socket.connect(('192.168.1.15', 8000))
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






