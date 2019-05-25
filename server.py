# import socket programming library 
import socket 

# import thread module 
from _thread import *
import threading 
import random

print_lock = threading.Lock() 

serv_ans = True

# thread fuction 
class NodeServer():
    def __init__(self, addr=None):
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
        self.sk.sendto(data, addr)

        while True: 

            # data received from client 
            packet, addr = self.sk.recvfrom(self.max_pack_legth) 
            print('Thread servidor recebendo de: ', addr[0], ':', addr[1])
            print(packet.decode())
            print(addr)
            ans = input('\nDo you want to continue(y/n) :') 
            if not packet: 
                print('Bye') 
                
                # lock released on exit 
                # print_lock.release() 
                break
            elif ans == 'exit':
                serv_ans = False
                break

            # reverse the given string from client 
            data = packet[::-1] 

            # send back reversed string to client 
            print('Thread servidor mandando para: ', addr[0], ':', addr[1])
            self.sk.sendto(data, addr) 

        # connection closed 
        self.sk.close()        


def Main(): 
    host = ""
    port = 12345
    addr1 = (host, port) 
    s = NodeServer(addr1)
    # a forever loop until client wants to exit 
    while serv_ans: 

        data, addr = s.sk.recvfrom(s.max_pack_legth)
        print('Primeira conexao :', addr[0], ':', addr[1]) 
        # Start a new thread and return its identifier 
        if data.decode() == "new":
            num = random.randint(49152, 65534)
            n = NodeServer(("", num))
            start_new_thread(n.thread_server, (addr,data)) 
    s.sk.close() 

if __name__ == '__main__': 
	Main() 
