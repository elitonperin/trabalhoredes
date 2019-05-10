import socket 

class Leecher():
    def __init__(self, args=None):
        self.port = 7001
        self.ip_broadcast = '192.168.100.255'
        pass

    def broadcast(self):
        cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        cs.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        cs.sendto('This is a test'.encode(),
                  (self.ip_broadcast, self.port))
        print('Broadcast enviado')

leecher = Leecher()
leecher.broadcast()

# ip = input('digite o ip de conexao: ') 
ip = '192.168.100.20'
port = 7001
addr = ((ip,port)) 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mensagem = input("digite uma mensagem para enviar ao servidor: ")
packet = bytearray(mensagem, 'utf8')
client_socket.sendto(packet, addr) 
print ('mensagem enviada' )
packet, addr = client_socket.recvfrom(1280)
print('Mensagem recebida: ', packet.decode())
client_socket.close()
