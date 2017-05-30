import struct
import socket
import io
import os
import time
import numpy as np 
import tensorflow as tf
from keras.models import model_from_json
import cv2

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

class RCControl(object):

	def __init__(self):
		# Initialize client for sending driving instructions to the RPi
		self.client_socket = socket.socket()
		self.client_socket.connect(('192.168.1.18', 8000))

	def steer(self, prediction):
		if (prediction == 0):
			key = "w"
		elif (prediction == 1):
			key = "a"
		elif (prediction == 2):
			key = "d"
		else:
			key = "space"
		self.client_socket.send(key.encode())

	def stop(self):
		key = "space"
		self.client_socket.send(key.encode())

	def sense(self):
		# Receive distance data from onboard ultrasonic sensor
		distance = struct.unpack("f", self.connection.recv(1024))
		return distance

	def close(self):
		self.client_socket.close()

class SelfDrive(object):

	def __init__(self):
		# Initialize some classes
		self.NVIDIA_model = NVIDIAModel()
		self.rc_car = RCControl()
		# Initialize server for receiving camera frames from the RPi
		self.server_socket = socket.socket()
		self.server_socket.bind(('0.0.0.0', 8000))
		self.server_socket.listen(0)
		# Accept a single connection and make a file-like object out of it
		self.connection, self.client_address = self.server_socket.accept()
		print("Connection from: ", self.client_address)
		self.connection = self.connection.makefile('rb')
		self.stream()

	def stream(self):
		try:
			print("Streaming...")
			start = time.time()
			frames = 0
			while True:
				# Read the length of the image as a 32-bit unsigned int. If the
				# length is zero, quit the loop
				image_len = struct.unpack('<L', self.connection.read(struct.calcsize('<L')))[0]
				if not image_len:
					break
				# Construct a stream to hold the image data and read the image
				# data from the connection
				image_stream = io.BytesIO()
				image_stream.write(self.connection.read(image_len))
				# Rewind the stream, open it as an image with OpenCV, convert to RGB
				image_stream.seek(0)
				data = np.fromstring(image_stream.getvalue(), dtype=np.uint8)
				image = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
				image = image.astype(np.float32)
				image = self.NVIDIA_model.process(image)
				prediction = self.NVIDIA_model.predict(image)
				# Get distance from ultrasonic sensor
				distance = self.rc_car.sense()
				# If the distance is below threshold, stop the car
				if distance is not None and distance < 30:
					self.rc_car.stop()
					print("Obstacle detected: stopping car")
				else:
					self.rc_car.steer(prediction)
				if cv2.waitKey(1) == ord('x'):
					break
				frames += 1

		finally:
			self.connection.close()
			self.server_socket.close()
			self.rc_car.close()

if __name__ == '__main__':
    SelfDrive()








