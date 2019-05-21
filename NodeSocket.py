# import socket programming library 
import socket 

# import thread module 
from _thread import *
import threading 
import random
import struct

print_lock = threading.Lock() 

# thread fuction 
class NodeSocket():
    def __init__(self, parent, addr=None):
        self.parent = parent
        self.max_pack_legth = 1280
        self.addr = addr
        self.sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sk.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
        self.sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if addr is not None:
            self.sk.bind(self.addr) 
            print("Criado novo socket UDP")
            print("Enderecos: ", addr[0], " : ", addr[1])
        else:
            self.sk.bind(('', 0))
            addr = self.sk.getsockname()
            print("Enderecos: ", addr[0], " : ", addr[1])

    def thread_server(self, addr, data): 
        print('Thread servidor mandando para: ', addr[0], ':', addr[1])
        n_seq = -1
        init_segm = 0
        final_segm = 0
        ack = 0
        nack = 0
        cmd = 'nop'
        data = b'TEXTO'
        packet = struct.pack('siiiii', 
                                       cmd,
                                       n_seq, 
                                       init_segm, 
                                       final_segm, 
                                       ack,
                                       nack,
                                       data )
        self.sk.sendto(packet, addr)

        while True: 

            # data received from client 
            packet, addr = self.sk.recvfrom(self.max_pack_legth)
            n_seq, init_segm, final_segm, ack, nack, cmd = struct.unpack('iiiiif', packet)
            print('Thread servidor recebendo de: ', addr[0], ':', addr[1])
            ans = input('\nDo you want to continue(y/n) :') 
            if not packet: 
                print('Bye') 
                
                # lock released on exit 
                # print_lock.release() 
                break
            elif ans == 'exit':
                break

            # reverse the given string from client 
            data = data[::-1] 

            # send back reversed string to client 
            print('Thread servidor mandando para: ', addr[0], ':', addr[1])
            self.sk.sendto(data, addr) 

        # connection closed 
        self.sk.close()

    def thread_client(self, data, addr):

        while True: 
            # ask the client whether he wants to continue 
            ans = input('\nO que vc quer :\n1-Buscar musica\n2 - sair') 
            if ans == '1':
                ans1 = input('\nDigita nome:\n') 
                ### busca

                print('Deseja baixar:\n (y/n):')
                ### baixa
                data = ans1.encode()
                print('Thread cliente mandando para: ', addr[0], ':', addr[1])
                self.sk.sendto(data, addr)

                # data received from client 
                packet, addr = self.sk.recvfrom(self.max_pack_legth) 
                print('Thread cliebte recebendo de: ', addr[0], ':', addr[1])
                print(packet.decode())
                print(addr)
            elif ans == '2': 
                break


        # connection closed 
        self.sk.close()