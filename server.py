# import socket programming library 
import socket 

# import thread module 
from _thread import *
import threading 

print_lock = threading.Lock() 

# thread fuction 
class NodeServer():
    def __init__(self, addr=None):
        self.max_pack_legth = 1280
        self.addr = addr
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if addr is not None:
            self.socket.bind(self.addr) 

    def threaded(self): 

        while True: 

            # data received from client 
            packet, addr = self.socket.recvfrom(self.max_pack_legth) 
            if not packet: 
                print('Bye') 
                
                # lock released on exit 
                # print_lock.release() 
                break

            # reverse the given string from client 
            data = packet[::-1] 

            # send back reversed string to client 
            self.socket.sendto(data, addr) 

        # connection closed 
        self.socket.close() 


def Main(): 
	host = "" 
	port = 12345
    addr1 = (host, port)
    
    s = NodeServer(addr1)

	print("socket is listening") 

	# a forever loop until client wants to exit 
	while True: 

		# lock acquired by client 
		# print_lock.acquire() 
        data, addr = s.socket.recvfrom(self.max_pack_length)
		print('Connected to :', addr[0], ':', addr[1]) 

		# Start a new thread and return its identifier 
		start_new_thread(self.threaded, (addr,)) 
	s.close() 


if __name__ == '__main__': 
	Main() 
