import socket
import threading
import os

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []
        self.initial_message_sent = False  # Flag to track if the initial message is sent
        self.receive_dir = "received_files"  # Directory to store received files

    def connect(self, peer_host, peer_port):
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection.connect((peer_host, peer_port))
            self.connections.append(connection)
            print(f"Connected to {peer_host}:{peer_port}")
            if not self.initial_message_sent:
                self.send_data("Hello from peer!")
                self.initial_message_sent = True
                # Send a file after the initial message
                self.send_file("sample.txt")
        except socket.error as e:
            print(f"Failed to connect to {peer_host}:{peer_port}. Error: {e}")

    def listen(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(10)
        print(f"Listening for connections on {self.host}:{self.port}")

        while True:
            connection, address = self.socket.accept()
            self.connections.append(connection)
            print(f"Accepted connection from {address}")
            # Receive and store the file
            self.receive_file(connection)

    def send_data(self, data):
        for connection in self.connections:
            try:
                connection.sendall(data.encode())
            except socket.error as e:
                print(f"Failed to send data. Error: {e}")

    def send_file(self, filename):
        for connection in self.connections:
            try:
                with open(filename, 'rb') as file:
                    file_data = file.read(1024)
                    while file_data:
                        connection.send(file_data)
                        file_data = file.read(1024)
                    # Send an end-of-file marker to indicate completion
                    connection.send(b"EOF")  # Corrected to send as bytes
                    print(f"File '{filename}' sent successfully")
            except FileNotFoundError:
                print(f"File '{filename}' not found")
            except socket.error as e:
                print(f"Failed to send file. Error: {e}")

    def receive_file(self, connection):
        try:
            os.makedirs(self.receive_dir, exist_ok=True)
            filename = os.path.join(self.receive_dir, "received_file.txt")
            with open(filename, 'wb') as file:
                while True:
                    file_data = connection.recv(1024)
                    if file_data == b"EOF":
                        break  # End of file received
                    file.write(file_data)
                print(f"File received and stored as '{filename}'")
        except Exception as e:
            print(f"Error receiving file: {e}")

    def start(self):
        listen_thread = threading.Thread(target=self.listen)
        listen_thread.start()

if __name__ == "__main__":
    # Create two Peer instances
    peer1 = Peer("127.0.0.1", 12345)
    peer2 = Peer("127.0.0.1", 54321)

    # Start listening for connections in separate threads
    peer1.start()
    peer2.start()

    # Connect peer1 to peer2 and vice versa
    peer1.connect("127.0.0.1", 54321)
    peer2.connect("127.0.0.1", 12345)
