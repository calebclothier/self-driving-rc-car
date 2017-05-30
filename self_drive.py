import struct
import socket
import socketserver
import threading
import io
import os
import time
import math
import numpy as np
import tensorflow as tf
from keras.models import model_from_json
import cv2

# Distance data from ultrasonic sensor
distance = " "

class NVIDIAModel(object):

    def __init__(self):
        model_name = input('Choose a model: ')
        with open('NVIDIA_model/{}.json'.format(model_name), 'r') as jfile:
            self.model = model_from_json(jfile.read())
        self.model.compile(optimizer='adam', loss='mse')
        self.model.load_weights('NVIDIA_model/{}.h5'.format(model_name))

    def crop(self, image):
        """Crop out the top part of the image"""
        image = image[130:220,:]
        return image

    def blur(self, image):
        """Apply a slight blur to the image"""
        image = cv2.GaussianBlur(image, (3,3), 0)
        return image

    def resize(self, image):
        """Resize the image in accordance with the nVidia paper model"""
        image = cv2.resize(image,(200, 66), interpolation=cv2.INTER_AREA)
        return image

    def normalize(self, image):
        """Returns a normalized image with feature values from -1.0 to 1.0."""
        return image / 127.5 - 1.

    def process(self, image):
        image = self.crop(image)
        image = self.blur(image)
        image = self.resize(image)
        image = np.expand_dims(image, axis=2)
        image = np.expand_dims(image, axis=0)
        return image

    def predict(self, image):
        """Returns the predicted action given one input image"""
        self.prediction = self.model.predict(image, batch_size=1, verbose=0)
        return np.argmax(self.prediction)

class HaarCascade(object):

    def __init__(self):
        # Initialize the cascade classifier using pre-trained xml file
        self.cascade = cv2.CascadeClassifier('training_data/stop_sign.xml')
        # Camera params
        self.alpha = 0
        self.v0 = 112.447936527
        self.ay = 247.53291599
        self.h = 15.5 - 10

    def detect(self, image):
        # y camera coordinate of the target point 'P'
        v = 0
        # Identify all stop signs in image
        self.stop_signs = self.cascade.detectMultiScale(
            image,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(20, 20),
            flags=cv2.CASCADE_SCALE_IMAGE)
        # Draw rectangle around stop sign
        for (x, y, width, height) in self.stop_signs:
            cv2.rectangle(image, (x+5, y+5), (x+width-5, y+height-5), (255, 255, 255), 2)
            v = y + height - 5
            cv2.putText(image, 'STOP', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return v

    def calculate_distance(self, v, x_shift, image):
        # Compute aselfnd return the distance from the target point to the camera
        distance = self.h / math.tan(self.alpha + math.atan((v - self.v0) / self.ay))
        if distance > 0:
            cv2.putText(image, "%.1fcm" % distance,
                (image.shape[1] - x_shift, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return distance

class UltrasonicSensorHandler(socketserver.BaseRequestHandler):

    # Initialize data variable
    data = " "

    def handle(self):
        # Initialize global distance variable
        global distance
        try:
            while self.data:
                # Receive distance measurement from Pi
                self.data = self.request.recv(1024)
                distance = int(self.data[0])
        finally:
            print("Connection closed on sensor thread")

class VideoStreamHandler(socketserver.StreamRequestHandler):

    # Initialize some classes
    NVIDIA_model = NVIDIAModel()
    cascade = HaarCascade()

    def steer(self, prediction):
        if (prediction == 0):
            key = "w"
        elif (prediction == 1):
            key = "a"
        elif (prediction == 2):
            key = "d"
        else:
            key = "space"
        self.wfile.write(key.encode())

    def stop(self):
        key = "space"
        self.wfile.write(key.encode())

    def handle(self):
        print("Streaming...")
        # Initialize some variables
        global distance
        d_stop_sign = 25
        stop_start = 0
        stop_end = 0
        stop_flag = False
        stop_sign_active = True
        time_after_stop = 0
        start = time.time()
        frame = 0
        try:
            while True:
                # Read the length of the image as a 32-bit unsigned int. If the
                # length is zero, quit the loop
                image_len = struct.unpack('<L', self.rfile.read(struct.calcsize('<L')))[0]
                if not image_len:
                    break
                # Construct a stream to hold the image data and read the image
                # data from the connection
                image_stream = io.BytesIO()
                image_stream.write(self.rfile.read(image_len))
                # Rewind the stream, open it as an image with OpenCV, convert to gray
                image_stream.seek(0)
                data = np.fromstring(image_stream.getvalue(), dtype=np.uint8)
                image = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
                # Image processing pipeline
                new_image = image.astype(np.float32)
                new_image = self.NVIDIA_model.process(new_image)
                prediction = self.NVIDIA_model.predict(new_image)
                # Get v param for stop sign detection
                v_param = self.cascade.detect(image)
                # Calculate stop sign distance
                if v_param > 0:
                    d_stop_sign = self.cascade.calculate_distance(v_param, 300, image)
                # If the distance is below threshold, stop the car
                if distance is not None and distance < 30:
                    self.stop()
                    if (frame % 20) == 0:
                        print("Obstacle detected: stopping car")
                # If a stop sign is detected, stop for 5 seconds
                elif 0 < d_stop_sign < 25 and stop_sign_active:
                    print("Stop sign ahead")
                    self.stop()
                    if stop_flag is False:
                        stop_start = time.time()
                        stop_flag = True
                    stop_end = time.time()
                    if (stop_end - stop_start) > 5:
                        print("Waited for 5 seconds")
                        stop_flag = False
                        stop_sign_active = False
                # Otherwise, just drive normally
                else:
                    self.steer(prediction)
                    d_stop_sign = 25
                    if stop_sign_active is False:
                        time_after_stop = time.time() - stop_end
                        if time_after_stop > 5:
                            stop_sign_active = True
                cv2.imshow("Frame", image)
                frame += 1
                if cv2.waitKey(1) == int(ord('x')):
                    break
                # Print FPS every 100 frames
                if (frame % 100) == 0:
                    fps = frame / (time.time() - start)
                    print("Frames per second: ", fps)
                    frame = 0
                    start = time.time()
        finally:
            print("Connection closed on camera thread")

class ThreadServer(object):

    def server_thread1(host, port):
        server = socketserver.TCPServer((host, port), VideoStreamHandler)
        server.serve_forever()

    def server_thread2(host, port):
        server = socketserver.TCPServer((host, port), UltrasonicSensorHandler)
        server.serve_forever()

    distance_thread = threading.Thread(target=server_thread2, args=('192.168.1.11', 8002))
    distance_thread.start()
    video_thread = threading.Thread(target=server_thread1('192.168.1.11', 8000))
    video_thread.start()
            
if __name__ == '__main__':
    ThreadServer()
    
