# Import socket module 
import socket 
from server import NodeServer

def Main(): 
	# local host IP '127.0.0.1' 
	host = '127.0.0.1'

	# Define the port on which you want to connect 
	port = 12345
	addr_send = (host,port)

	s = NodeServer()

	message = "shaurya says geeksforgeeks"
	while True: 

		# message sent to server 
		s.sendto(message.encode('ascii'), addr_send) 

		# messaga received from server 
		data = s.recv(1024) 

		# print the received message 
		# here it would be a reverse of sent message 
		print('Received from the server :',str(data.decode('ascii'))) 

		# ask the client whether he wants to continue 
		ans = input('\nDo you want to continue(y/n) :') 
		if ans == 'y': 
			continue
		else: 
			break

if __name__ == '__main__': 
	Main() 
