import socket 

# ip = input('digite o ip de conexao: ') 
ip = '127.0.0.1'
port = 7001 
addr = ((ip,port)) 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
client_socket.connect(addr) 
mensagem = input("digite uma mensagem para enviar ao servidor: ")
packet = bytearray(mensagem, 'utf8')
client_socket.send(packet) 
print ('mensagem enviada' )
packet = client_socket.recv(1280)
print('Mensagem recebida: ', packet.decode())
client_socket.close()
