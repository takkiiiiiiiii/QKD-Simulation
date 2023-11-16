from http import client
import socket
import pickle
import time
import threading
from bb84 import sample_random_bit, measure_qubit_using_basis
from interface import QuantumDevice
from simulator import KET_0, SingleQubitSimulator
from distutils.util import strtobool



# Key
siftedKey = []

# key length
keyLength = 2048

# サーバーのIPアドレスとポート
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12001

# クライアントソケットを作成
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))

bob_device = SingleQubitSimulator()

def bool_to_bytes(bool_value) -> bool:
    if bool_value:
        return b'True'
    else:
        return b'False'

# サーバーからのデータを受信する関数
while(True):
    try:       
        serialized_qubit = client_socket.recv(1024)
        qubit = pickle.loads(serialized_qubit)
        # print(qubit.state)
        
        
        # generate bob's basis and bit
        bob_basis = sample_random_bit(bob_device)
        
        # measure a qubit using bob's basis
        judge = measure_qubit_using_basis(qubit, bob_basis)

        # send bob's basis through classical channel
        client_socket.send(bool_to_bytes(bob_basis))

        # Notification of whether the basis is equal to each other.
        resp = client_socket.recv(1024).decode('utf-8')

        if resp == 'Yes':
            if judge == strtobool('True'):
                siftedKey.append(int(qubit.bit))
                if len(siftedKey) == keyLength:
                    break
            else:
                # discard
                continue
        elif resp == 'No': 
            continue
    except ConnectionResetError:
        print("Server was closed")
        break  # サーバーがクローズされた場合、breakしてループを終了

print(siftedKey)

def receive():
    while True:
        try:
            encoded_message = client_socket.recv(1024).decode('utf-8')
            bit_array = [int(bit) for bit in encoded_message]
            for j in range(len(bit_array)):
                bit_array[j] = bit_array[j] ^ siftedKey[j]
            byte_array = bytes([int(''.join(map(str, bit_array[i:i+8])), 2) for i in range(0, len(bit_array), 8)])
            decrypted_message = byte_array.decode('utf-8')
            print(f"\nMessages received: {decrypted_message}")
            print("\nPlease enter the message to be sent : ", end='')
        except ConnectionResetError:
            print("Connection to the server has been lost.")
            break 

# 新しいスレッドでメッセージを受信する
threading.Thread(target=receive).start()



while(True):
    message = input("\nPlease enter the message to be sent : ")
    bit_values = ''.join(format(ord(char), '08b') for char in message)
    bit_array = [int(bit) for bit in bit_values]
    for j in range(len(bit_array)):
        bit_array[j] = bit_array[j] ^ siftedKey[j]
    
    encoded_massage = ''.join(map(str, bit_array))
    client_socket.send(encoded_massage.encode('utf-8'))
