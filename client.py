# Import socket module 
import socket 
from server import NodeServer
import random
# import thread module 
from _thread import *
import time
import threading 

def Main(): 
	# local host IP '127.0.0.1' 
	host = '127.0.0.1'

	# Define the port on which you want to connect 
	port = 12345
	addr_send = (host,port)

	s = NodeServer()

	message = "new"
	# message sent to server 
	s.sk.sendto(message.encode(), addr_send) 

	
	data, addr = s.sk.recvfrom(s.max_pack_legth) 
	# messaga received from server 
	# print the received message 
	# here it would be a reverse of sent message 
	print('Primeira conexao :', str(data.decode()))
	num = random.randint(49152, 65534)
	n = NodeServer(("", num))
	start_new_thread(n.thread_client, (data, addr)) 
	running = True
	while running:
		ans = input("Ver rede: ")
		if ans == 'exit':
			running = False

if __name__ == '__main__': 
	Main() 
