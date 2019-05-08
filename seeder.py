import socket 

class Seeder():
    def __init__(self, host='127.0.0.1', 
                 port=7001,
                 users_listen=10 ):
        self.host = host
        self.port = port 
        self.addr = (host, port) 
        self.serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_socket.bind(self.addr) 
        self.serv_socket.listen(users_listen) 

    def sequencial_transmission(self):
        pass
    
    def random_transmission(self):
        pass

    def seq_random_transmission(self):
        pass

    def run_server(self):
        var_exit = True

        while var_exit:
            print ('aguardando conexao')
            con, client = self.serv_socket.accept() 
            print ('conectado com: ', str(client)) 
            print ("aguardando mensagem")
            packet = con.recv(1280) 
            print ("mensagem recebida: "+ packet.decode())
            con.send(packet)
            if packet.decode() == 'exit':
                var_exit = False
                print("Fechando servidor")

        self.serv_socket.close()

if __name__ == "__main__":
    server = Seeder()
    server.run_server()
    exit()