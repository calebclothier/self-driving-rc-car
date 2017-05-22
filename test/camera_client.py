import io
import socket
import struct
import time
import picamera

class CameraClient(object):
	
	def __init__(self, stream_length):
		# Connect a client socket to the Macbook-based server
		self.client_socket = socket.socket()
		self.client_socket.connect(('192.168.1.15', 8000))
		# Make a file-like object out of the connection
		self.connection = self.client_socket.makefile('wb')
		self.stream_length = stream_length
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
				self.connection.write(struct.pack('<L', stream.tell()))
				self.connection.flush()
				# Rewind the stream and send image data through
				stream.seek(0)
				self.connection.write(stream.read())
				# End stream after 30 seconds
				if time.time() - start > self.stream_length:
					break
				# Reset stream for next capture
				stream.seek(0)
				stream.truncate()
			# Write a length of 0 to the stream to signal we're done
			self.connection.write(struct.pack('<L', 0))
		finally:
			self.connection.close()
			self.client_socket.close()

if __name__ == '__main__':
	CameraClient(30)

