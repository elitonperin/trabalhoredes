import socket 
import time
import os
import argparse

class Seeder():
    def __init__(self, host='127.0.0.1', 
                 port=7001,
                 sharead_path='.',
                 args=None):
        if args.port is not None:
            self.port=args.port
        else:
            self.port = port
        if args.path is not None:
            self.sharead_path=args.path
        else:
            self.sharead_path = sharead_path


        if args.host is not None:
            if args.host == 'find':
                self.host = self.get_my_local_ip()
            else:
                self.host = args.host
        else:
            self.host = host 
        
        self.addr = (self.host, self.port)
        print('Meu endereco: ', self.addr) 
        self.serv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
        self.serv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serv_socket.bind(self.addr) 

    def get_files_for_share(self):
        caminhos = [os.path.join(self.sharead_path, nome) for nome in os.listdir(self.sharead_path)]
        arquivos = [arq.split('\\')[-1] for arq in caminhos if os.path.isfile(arq)]
        return arquivos

    def get_my_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))

        data_addr = s.getsockname()
        print("IP local: ", data_addr[0])
        s.close()
        return data_addr[0]

    def split_files(self):
        pass

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
            print ("aguardando mensagem")
            packet, addr = self.serv_socket.recvfrom(1280) 
            print ('recebido de: ', str(addr)) 
            print ("mensagem recebida: "+ packet.decode())
            #dormir por 20 ms
            time.sleep(.020)
            self.serv_socket.sendto(packet, addr)
            if packet.decode() == 'exit':
                var_exit = False
                print("Fechando servidor")

        self.serv_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="testing btpeer.py")
    parser.add_argument("--port", type=int)
    parser.add_argument("--host", type=str)
    parser.add_argument("--path", type=str)
    args = parser.parse_args()

    server = Seeder(args=args)
    
    print(server.get_files_for_share())
    server.run_server()
    
    exit()
