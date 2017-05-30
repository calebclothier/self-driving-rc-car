import struct
import socket
import time, sys, termios, tty
import io
import os
import numpy as np
import cv2

class CollectTrainingData(object):

    def __init__(self):
        # Initialize client for sending driving instructions to the RPi
        self.client_socket = socket.socket()
        self.client_socket.connect(('192.168.1.18', 8000))
        # Initialize server for receiving camera frames from the RPi
        self.server_socket = socket.socket()
        self.server_socket.bind(('0.0.0.0', 8000))
        self.server_socket.listen(0)
        # Accept a single connection and make a file-like object out of it
        self.connection, self.client_address = self.server_socket.accept()
        self.connection = self.connection.makefile('rb')
        # Set up numpy array for training labels
        self.train_labels = np.zeros((1, 4))
        self.temp_label = np.zeros((4, 4))
        for i in range(4):
            self.temp_label[i,i] = 1
        self.run_number = int(input('What number run is this? '))
        os.makedirs('training_images/run_{}'.format(self.run_number))
        # Start the stream
        self.stream()

    def get_keys(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key

    def stream(self):
        try:
            frame = 0
            print("Connection from: ", self.client_address)
            print("Streaming...")
            while True:
                # Get key input, add to label array, and send to the RPi
                key = self.get_keys()
                self.client_socket.send(key.encode())
                if (key == "w"):
                    self.train_labels = np.vstack((self.train_labels, self.temp_label[0]))
                    last = self.temp_label[0]
                elif (key == "a"):
                    self.train_labels = np.vstack((self.train_labels, self.temp_label[1]))
                    last = self.temp_label[1]
                elif (key == "d"): 
                    self.train_labels = np.vstack((self.train_labels, self.temp_label[2]))
                    last = self.temp_label[2]
                elif (key == "space"):
                    self.train_labels = np.vstack((self.train_labels, self.temp_label[3]))
                    last = self.temp_label[3]
                elif (key == 'x'):
                    break
                else:
                    self.train_labels = np.vstack((self.train_labels, last))
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
                #image = cv2.imdecode(data, cv2.IMREAD_COLOR)
                # Save the image
                if frame > 0:
                    cv2.imwrite('training_images/run_%d/frame_%d.jpg'%(self.run_number, frame), image)
                # Show the image
                cv2.imshow("Frame", image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                # Increase frame number
                frame += 1

            # Save the label array
            self.train_labels = self.train_labels[1:, :]
            os.makedirs('training_labels/run_{}'.format(self.run_number))
            np.save('training_labels/run_{}/labels.npy'.format(self.run_number), self.train_labels)
            # Print some stats
            print('\nNumber of training labels: '+str(self.train_labels.shape[0]))
            print('Number of frames: '+str(frame))

        finally:
            self.connection.close()
            self.server_socket.close()
            self.client_socket.close()

if __name__ == '__main__':
    CollectTrainingData()


