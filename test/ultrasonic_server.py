import socket
import struct
import time

class UltrasonicServer(object):

    def __init__(self):
        self.server_socket = socket.socket()
        self.server_socket.bind(('0.0.0.0', 8002))
        self.server_socket.listen(0)
        # Accept a single connection and start streaming
        self.connection, self.client_address = self.server_socket.accept()
        self.stream()

    def stream(self):
        try:
            print("Connection from: ", self.client_address)
            print("Streaming...")
            print("Press 'q' to exit")
            start = time.time()
            while True:
                distance = struct.unpack("f", self.connection.recv(1024))
                if not distance:
                    break
                print("Distance: %.1f" % distance)
                # Break connection after 10 seconds of testing
                if time.time() - start > 10:
                    break
        finally:
            self.connection.close()
            self.server_socket.close()

if __name__ == '__main__':
    UltrasonicServer()


