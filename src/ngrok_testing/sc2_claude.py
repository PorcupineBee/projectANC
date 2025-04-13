import socket
import threading

def handle_client(client_socket, address):
    print(f"Connection established with {address}")
    try:
        # Receive data from the client
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            
            print(f"Received from Colab: {data}")
            
            # Send a response back
            response = f"Server received: {data}"
            client_socket.send(response.encode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        print(f"Connection with {address} closed")

def start_server(port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    print(f"Server listening on port {port}")
    
    try:
        while True:
            client_socket, address = server.accept()
            client_handler = threading.Thread(
                target=handle_client,
                args=(client_socket, address)
            )
            client_handler.daemon = True
            client_handler.start()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()