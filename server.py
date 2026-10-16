import socket
import threading
import os
import select

# Сервер слушает порт, выданный хостингом Render
SERVER_PORT = int(os.environ.get("PORT", 10000))

def handle_socks5(client_sock):
    try:
        # 1. Приветствие (Handshake) от клиента
        version, nmethods = client_sock.recv(2)
        methods = client_sock.recv(nmethods)
        client_sock.sendall(b"\x05\x00") # Отвечаем: SOCKS5, аутентификация не нужна

        # 2. Получаем запрос на подключение от игры
        cmd, atyp = client_sock.recv(4)[1:3]
        
        if atyp == 1: # IPv4 адрес
            target_host = socket.inet_ntoa(client_sock.recv(4))
        elif atyp == 3: # Доменное имя (например, roblox.com)
            domain_len = client_sock.recv(1)[0]
            target_host = client_sock.recv(domain_len).decode()
        else:
            client_sock.close()
            return
            
        target_port = int.from_bytes(client_sock.recv(2), 'big')

        # Подключаемся к игровому серверу Roblox из Европы
        if cmd == 1: # CONNECT (TCP)
            remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_sock.connect((target_host, target_port))
            client_sock.sendall(b"\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00")
        else:
            client_sock.close()
            return

        # 3. Пересылаем пакеты в обе стороны без потерь
        while True:
            r, w, x = select.select([client_sock, remote_sock], [], [])
            if client_sock in r:
                data = client_sock.recv(16384)
                if not data: break
                remote_sock.sendall(data)
            if remote_sock in r:
                data = remote_sock.recv(16384)
                if not data: break
                client_sock.sendall(data)
    except: pass
    finally:
        try: client_sock.close()
        except: pass

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", SERVER_PORT))
    server.listen(200)
    print(f"BOOSTERFPS SOCKS5 Engine active on port {SERVER_PORT}...")
    while True:
        try:
            client_sock, addr = server.accept()
            threading.Thread(target=handle_socks5, args=(client_sock,), daemon=True).start()
        except: pass
