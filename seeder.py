import socket 
import time
import os
import argparse
from pygame import mixer
import pyaudio
import wave
import sys

class Seeder():
    def __init__(self, host='127.0.0.1', 
                 port=7001,
                 sharead_path='.',
                 args=None):
        self.max_data_legth = 1280
        self.ext_files = ['wav']
        self.APP_KEY = 'APP_KEY'
        self.header_size = 4
        
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

    def get_only_music_files(self):
        files = self.get_files_for_share()
        return [ music_file for music_file in files if music_file.split('.')[1] in self.ext_files ]

    def get_my_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))

        data_addr = s.getsockname()
        print("IP local: ", data_addr[0])
        s.close()
        return data_addr[0]

    def split_files(self, name_file):
        size = os.path.getsize(name_file)
        size_data = size/(self.max_data_legth - self.header_size)
        f = open(name_file, 'rb')
        # data = f.read(int(size_data))
        data = f.read()
        self.play_audio(data)
        f.close()
        pass

    def play_audio(self, data):
        
        chunk = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 50000

        p = pyaudio.PyAudio()

        stream = p.open(format = FORMAT,
                        channels = CHANNELS,
                        rate = RATE,
                        input = True,
                        output = True,
                        frames_per_buffer = chunk)

        for i in range(0, len(data), chunk):
            stream.write(data[i:i+chunk])
        stream.stop_stream()
        stream.close()

        p.terminate()

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
            packet, addr = self.serv_socket.recvfrom(self.max_data_legth) 
            print ('recebido de: ', str(addr)) 
            print ("mensagem recebida: "+ packet.decode())
            #dormir por 20 ms
            packet = self.get_only_music_files()
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
    
    # print(server.get_only_music_files())
    # server.run_server()
    server.split_files(server.get_only_music_files()[0])

    
    exit()
