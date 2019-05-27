import socket 
import time
import os
import stat
import argparse
import pyaudio
import wave
import struct
import sys
import random
from NodeSocket import NodeSocket
from _thread import *
import threading 

SERVER_ON = True

# thread fuction 
class NodeServer():
    def __init__(self, parent, addr=None):
        self.parent = parent
        self.max_pack_legth = 1280
        self.addr = addr
        self.transmission_opt = 'rand'
        self.transmission_opt = 'srand'
        self.transmission_opt = 'simple'
        self.transmission_opt = 'seq'
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
    
    def sequencial_transmission(self, init, end, cmd, num_seq, data, size_data, addr):
        pass
    
    def random_transmission(self, init, end, cmd, num_seq, data, size_data, addr):
        pass

    def seq_random_transmission(self, init, end, cmd, num_seq, data, size_data, addr):
        pass
        
    def normal_transmission(self, init, end, cmd, num_seq, data, size_data, addr):
        i = init
        while i*self.parent.data_size < end:
            send_header = struct.pack('3siiii', cmd, num_seq+1, size_data, init, end)
            time.sleep(0.02)
            send_packet = send_header + data[i]
            self.sk.sendto(send_packet, addr)
            i=i+1
            recv_packet, addr = self.sk.recvfrom(self.max_pack_legth)
            recv_header = recv_packet[:20]
            cmd, num_seq, size_data, init, end = struct.unpack('3siiii', recv_header)
            recv_data = recv_packet[20:]
            song_name = recv_data.decode()

    def send_file(self, cmd, addr, recv_packet):
        
        recv_header = recv_packet[:20]
        cmd, num_seq, size_data, init, end = struct.unpack('3siiii', recv_header)
        recv_data = recv_packet[20:]
        song_name = recv_data.decode()
        finish = False
        self.parent.header_size = 20
        data, num_of_packs, size = self.parent.split_files(song_name)

        if self.transmission_opt == 'seq':
            self.sequencial_transmission(init, end, cmd, num_seq, data, size_data, addr)
        elif self.transmission_opt == 'rand':
            self.random_transmission(init, end, cmd, num_seq, data, size_data, addr)
        elif self.transmission_opt == 'srand':
            self.seq_random_transmission(init, end, cmd, num_seq, data, size_data, addr)
        else:
            self.normal_transmission(init, end, cmd, num_seq, data, size_data, addr)
        
        pass

    def thread_server(self, addr, data): 
        print('Thread servidor mandando para: ', addr[0], ':', addr[1])
        self.sk.sendto(data, addr)
        send_header = ''
        send_data = ''

        while True: 

            # data received from client 
            recv_packet, addr = self.sk.recvfrom(self.max_pack_legth) 
            print('Thread servidor recebendo de: ', addr[0], ':', addr[1])
            # print('Mensagem: ', recv_packet.decode())

            recv_header = recv_packet[:12]
            recv_data = recv_packet[12:]

            cmd, num_seq, size_data = struct.unpack('3sii', recv_header)
            print(cmd)
            if cmd == b'ext':
                print('Saindo')
                self.parent.quit()
            elif cmd == b'req':
                print('Sendo requisitado')
                has, size_file = self.parent.request_file(recv_data, size_data, addr)
                if has:
                    header = struct.pack('3sii', b'yes', num_seq+1, size_data)
                    data_send = struct.pack('i', size_file)
                else:
                    header = struct.pack('3sii', b'not', num_seq+1, size_data)
                    data_send = struct.pack('i', 0)
            elif cmd == b'dow':
                print('Fazendo upload')
                self.send_file(cmd, addr, recv_packet)
                header = struct.pack('3siiii', b'fin',  num_seq+1, size_data, 0, 0)
                data_send = struct.pack('i', 0)
                var_exit = False
            elif cmd == b'exi':
                print('Saindo')
                self.sk.close()
                self.parent.quit()
            else:
                print('Comando Invalido!')
            # self.sk.sendto(recv_packet, addr)
            print(sys.getsizeof(header))
            print(sys.getsizeof(data_send))
            send_packet = header + data_send
            # send back reversed string to client 
            print('Thread servidor mandando para: ', addr[0], ':', addr[1])
            #print('Send packet with: ', send_packet.decode())
            self.sk.sendto(send_packet, addr) 

        # connection closed 

class Seeder():
    def __init__(self, host='127.0.0.1', 
                 port=7001,
                 sharead_path='.',
                 args=None):
        self.max_pack_legth = 1280
        self.ext_files = ['wav', 'mp3']
        self.APP_KEY = 'APP_KEY'
        self.header_size = 4
        self.nodes_of_connections = []
        
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
        #retorna o tamanho em bytes
        size = os.path.getsize(name_file)
        self.data_size = self.max_pack_legth - self.header_size
        num_of_packs = size/self.data_size
        data_vector = []
        i = 0
        f = open(name_file, 'rb')
        while i < num_of_packs:
            data_vector.append(f.read(self.data_size))
            i=i+1
        f.close()
        # self.play_audio(data)
        print(size, self.header_size, self.max_pack_legth, num_of_packs)
        return data_vector, num_of_packs, size


    def setup_player(self):
        self.chunk = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 50000
             
        self.player = pyaudio.PyAudio()

        self.stream = self.player.open(format = FORMAT,
                        channels = CHANNELS,
                        rate = RATE,
                        input = True,
                        output = True,
                        frames_per_buffer = self.chunk)

    def finish(self):
        self.stream.close()
        self.player.terminate()

    def play_audio(self, data):

        for i in range(0, len(data), self.chunk):
            self.stream.write(data[i:i+self.chunk])
        self.stream.stop_stream()

    def run_server(self):
        # a forever loop until client wants to exit 
        self.connect_count = 0

        while SERVER_ON: 
            packet, addr = self.serv_socket.recvfrom(self.max_pack_legth) 
            self.connect_count += 1
            print('Conexao n:', self.connect_count)
            print('Com endereco: ', addr[0], ':', addr[1]) 
            # Start a new thread and return its identifier 
            if packet.decode() == self.APP_KEY:
                num = random.randint(49152, 65534)
                n = NodeServer(self, ("", num))
                self.nodes_of_connections.append(n)
                start_new_thread(n.thread_server, (addr, packet)) 
        self.serv_socket.close()
    
    def state1(self):
        pass
        
    def request_file(self, name, size_data, addr):
        print('Request file: ', name)
        song_name = name.decode()
        print(song_name)
        print(self.get_only_music_files())
        if song_name in self.get_only_music_files():
            file_stats = os.stat(os.path.join(self.sharead_path, song_name))
            print('Tem, mandando info')
            return True, file_stats[stat.ST_SIZE]
        else:
            return False, None

    def send_file(self, comando, addr, recv_packet):
        recv_header = recv_packet[:14]
        cmd, num_seq, size_data, init, end = struct.unpack('3siiii', recv_header)
        recv_data = recv_packet[14:]
        song_name = recv_data.decode()
        print(song_name)
        self.header_size = 14
        data, num_of_packs, size = self.split_files(song_name)
        msg = [num_of_packs, size]
        print(data[0])
        msg = struct.pack('fii', num_of_packs, size, self.data_size)
        self.serv_socket.sendto(msg, addr)
        
        i = 0
        while i < num_of_packs:
            time.sleep(0.02)
            self.serv_socket.sendto(data[i], addr)
            i=i+1

        pass

    def quit(self):
        print("Fechando servidor")
        self.serv_socket.close()
        exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="testing btpeer.py")
    parser.add_argument("--port", type=int)
    parser.add_argument("--host", type=str)
    parser.add_argument("--path", type=str)
    args = parser.parse_args()

    server = Seeder(args=args)
    
    server.run_server()

    
    # a forever loop until client wants to exit 
    # while True: 

    #     # lock acquired by client 
    #     # print_lock.acquire() 
    #     packet, addr = server.serv_socket.recvfrom(server.max_pack_legth)
    #     cmd, n_seq, init_segm, final_segm, ack, nack, data = struct.unpack('3s i i i i i s', packet)
    #     print('Primeira conexao :', addr[0], ':', addr[1]) 
    #     print(cmd, data)
    #     # Start a new thread and return its identifier

    #     if cmd == "new":
    #         num = random.randint(49152, 65534)
    #         n = NodeSocket(server, ("", num))
    #         start_new_thread(n.thread_server, (addr,packet)) 
    # server.serv_socket.close() 
    
    # print(server.get_only_music_files())
    # server.split_files(server.get_only_music_files()[0])

    
    exit()
