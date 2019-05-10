import socket 

max_data_legth = 1280
class SeederInfo():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.addr = (ip, port)
        self.list_of_musics = []

class Leecher():
    def __init__(self, args=None):
        self.port = 7001
        self.ip_broadcast = '192.168.1.255'
        self.max_data_legth = 1280
        self.list_seeders = []
        self.APP_KEY = 'APP_KEY'
        
        self.cli_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.cli_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.cli_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        pass

    def broadcast(self):
        self.cli_socket.sendto(self.APP_KEY.encode(),
                  (self.ip_broadcast, self.port))
        print('Broadcast enviado')
        msg, addr = self.cli_socket.recvfrom(self.max_data_legth)
        s = SeederInfo(ip=addr[0], port=addr[1])
        self.list_seeders.append(s)
        return addr

    def init_socket(self):
        pass

    def run_client(self):
        msg = input("digite uma mensagem para enviar ao servidor: ")
        self.cli_socket.sendto(msg.encode(), self.list_seeders[0].addr) 
        print ('mensagem enviada' )
        packet, addr = self.cli_socket.recvfrom(max_data_legth)
        print('Mensagem recebida: ', packet.decode())
        self.cli_socket.close()

    def request_file(self):
        pass

leecher = Leecher()
ip, port = leecher.broadcast()
leecher.run_client()
