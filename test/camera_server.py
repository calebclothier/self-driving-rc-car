import io
import struct
import socket
import cv2
import numpy as np

class CameraServer(object):

    def __init__(self):
        self.server_socket = socket.socket()
        self.server_socket.bind(('0.0.0.0', 8000))
        self.server_socket.listen(0)
        # Accept a single connection and make a file-like object out of it
        self.connection, self.client_address = self.server_socket.accept()
        self.connection = self.connection.makefile('rb')
        self.stream()

    def stream(self):
        try:
            print("Connection from: ", self.client_address)
            print("Streaming...")
            print("Press 'q' to exit")
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
                self.image = cv2.imdecode(data, 1)
                #self.image = self.image[:, :, ::-1]
                cv2.imshow("Frame", self.image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            self.connection.close()
            self.server_socket.close()

if __name__ == '__main__':
    CameraServer()
