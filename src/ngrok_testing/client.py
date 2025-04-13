import socket

# Use the ngrok forwarding address
host = '0.tcp.ngrok.io'  # from ngrok output
port = 19345             # from ngrok output

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

client_socket.sendall(b"Hello from Colab!")
data = client_socket.recv(1024)

print("Received from server:", data.decode())

client_socket.close()
