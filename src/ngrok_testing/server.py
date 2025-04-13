import socket

# HOST = '127.0.0.1'
HOST = '0.0.0.0'
PORT = 9999

# Create TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(2)
print(f"Listening on {HOST}:{PORT}...")

conn, addr = server_socket.accept()
print(f"Connected by {addr}")

# Simple message exchange
while True:
    data = conn.recv(1024)
    if not data:
        print("Connection closed.")
        break

    print("Client:", data.decode())
    response = input("Server: ")
    conn.sendall(response.encode())

conn.close()
server_socket.close()


# "C:/Users/shanu/anaconda3/envs/ANCpy311/python.exe"