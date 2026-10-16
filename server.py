import socket
import threading
import os

SERVER_HOST = "0.0.0.0"
SERVER_PORT = int(os.environ.get("PORT", 10000))

def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(16384)
            if not data: break
            client_socket.sendall(data)
    except: pass
    finally: client_socket.close()

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(100)
    print(f"BOOSTERFPS Core running on port {SERVER_PORT}...")
    while True:
        try:
            client_sock, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()
        except: pass
