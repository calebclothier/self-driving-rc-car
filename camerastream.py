import io
import socket
import struct
import time
import picamera

def connect():
    # Connect a client socket to the Macbook-based server
    client_socket = socket.socket()
    client_socket.connect(('192.168.1.255', 8000))

def stream(stream_length):
    # Make a file-like object out of the connection
    connection = client_socket.makefile('wb')
    try:
        camera = picamera.PiCamera()
        camera.resolution(640, 480)
        # Start a preview and let camera warm up
        camera.start_preview()
        time.sleep(2)

        start = time.time()
        stream = io.BytesIO()
        for foo in camera.capture_continuous(stream, 'jpeg'):
            # Write the length of the capture to the stream
            # and flush to make sure it gets sent
            connection.write(struct.pack('<L', stream.tell()))
            connection.flush()
            # Rewind the stream and send image data through
            stream.seek(0)
            connection.write(stream.read())
            # End stream after 30 seconds
            if time.time() - start > stream_length:
                break
            # Reset stream for next capture
            stream.seek(0)
            stream.truncate()
        # Write a length of 0 to the stream to signal we're done
        connection.write(struct.pack('<L', 0))
    finally:
        connection.close()
        client_socket.close()

