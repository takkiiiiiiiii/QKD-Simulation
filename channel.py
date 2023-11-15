import socket
import threading

# サーバーのIPアドレスとポート
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12001

# クライアントからの接続を待機する関数
def handle_client(client_socket, addr):
    print(f"[*] 新しい接続を受け入れました: {addr[0]}:{addr[1]}")
    try:
        while True:
            # クライアントからのデータを受信
            data = client_socket.recv(1024)
            if not data:
                break

            # 他のクライアントにデータを送信
            for client in clients:
                if client != client_socket:
                    client.send(data)

    except ConnectionResetError:
        print(f"[*] {addr[0]}:{addr[1]} からの接続が切断されました")
    finally:
        client_socket.close()

# サーバーソケットを作成
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(2)  # 最大2つの接続を許可

print("[*] サーバーが起動しました")

clients = []  # 接続されたクライアントを保持するリスト

while len(clients) < 2:
    client, addr = server_socket.accept()
    clients.append(client)
    print(f"[*] クライアント{len(clients)}が接続しました: {addr[0]}:{addr[1]}")
    threading.Thread(target=handle_client, args=(client, addr)).start()
