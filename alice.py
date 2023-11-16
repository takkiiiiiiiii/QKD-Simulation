import socket
import threading
import pickle
from tkinter import W
from bb84 import generate_alice_basis_and_bit_and_qubit, measure_qubit_using_basis
from interface import Qubit
from interface import QuantumDevice
from simulator import SingleQubitSimulator, KET_0
from distutils.util import strtobool

import qkd

# Key
siftedKey = []

# key length
keyLength = 2048

# Channel
QUANTUM_CHANNEL = []
CLASSICAL_CHANNEL = []

# サーバーのIPアドレスとポート
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12001

time = 0

# クライアントソケットを作成
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))

alice_device = SingleQubitSimulator()


# サーバーからのデータを受信する関数
while(True):
    try:
        time += 1
        alice_bit, alice_basis, qubit = generate_alice_basis_and_bit_and_qubit(alice_device)
        qubit.basis = alice_basis
        qubit.bit = alice_bit
    
        serialized_qubit = pickle.dumps(qubit)
        client_socket.send(serialized_qubit)
    
        bob_basis = client_socket.recv(1024).decode('utf-8')

        if alice_basis == strtobool(bob_basis):
            client_socket.send('Yes'.encode('utf-8'))
            judge = measure_qubit_using_basis(qubit, alice_basis)
            siftedKey.append(int(qubit.bit))
            if len(siftedKey) == keyLength:
                break
        else:
            client_socket.send('No'.encode('utf-8'))
    
    except ConnectionResetError:
        print("Server was closed")
        break

print(siftedKey)
print(f'repeted {time} times')

def bool_to_bytes(bool_value) -> bool:
    if bool_value:
        return b'True'
    else:
        return b'False'
    

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


