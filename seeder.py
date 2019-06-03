# modulo para conexao
import socket 

# modulo para audio
import pyaudio
import wave

# modulo para utilidades
import time
import os
import stat
import argparse
import struct
import sys
import random
import logging
from datetime import datetime

# modulo para threads
from _thread import *
import threading 

SERVER_ON = True

# thread fuction 
class NodeServer():
    def __init__(self, parent, addr=None):
        self.parent = parent
        self.max_pack_legth = 1280
        self.addr = addr
        self.transmission_opt = 'srand'
        self.transmission_opt = 'simple'
        self.transmission_opt = 'seq'
        self.transmission_opt = 'rand'
        self.sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sk.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
        self.sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if addr is not None:
            self.sk.bind(self.addr)             
        else:
            self.sk.bind(('', 0))
            addr = self.sk.getsockname()
        logging.info("Criado novo socket UDP")
        logging.info("Enderecos: " + addr[0] + " : " + str(addr[1]))
    
    def sequencial_transmission(self, init, end, cmd, num_seq, data, size_data, addr):
        logging.info("Sequential transmission")
        header_size = self.parent.header_size
        size_data_send = self.parent.data_size
        i = init
        num_seq_send = num_seq
        num_pack = end
        prob = 1-self.parent.R
        logging.info("Probabilidade de nao enviar com: " + str(prob))
        while i < num_pack:
            if random.random() > prob:
                packet_avaliable = True
            else:
                packet_avaliable = False
            if packet_avaliable:
                pos_pack = i
                send_header = struct.pack('3siiiii', cmd, pos_pack, num_seq_send+1, size_data_send, init, end)
                # print( unicode( send_header.decode(), 'utf-8'))
                send_packet = send_header + data[i]
                self.sk.sendto(send_packet, addr)
                recv_packet, addr = self.sk.recvfrom(self.max_pack_legth)
                recv_header = recv_packet[:header_size]
                cmd, pos_pack, num_seq, size_data, init, end = struct.unpack('3siiiii', recv_header)
                if num_seq != num_seq_send:
                    i=i+1
                    num_seq_send = num_seq
                else:
                    logging.warn("Pacote n: "+ str(pos_pack) + ' PERDIDO!')
                recv_data = recv_packet[header_size:]
                song_name = recv_data.decode()
            else:
                time.sleep(0.02)
        send_header = struct.pack('3siiiii', b'fin', pos_pack, num_seq+1, size_data, 0, 0)
        data_send = struct.pack('i', 0)
        send_packet = send_header + data_send
        self.sk.sendto(send_packet, addr)
        logging.info('Arquivo enviado')

    
    def random_transmission(self, init, end, cmd, num_seq, data, size_data, addr):
        logging.info("Random transmission")
        header_size = self.parent.header_size
        size_data_send = self.parent.data_size
        i = init
        num_pack = end
        list_packs = list(range(init, end))
        list_choice = []
        num_seq_sender = num_seq
        while i < num_pack:
            choice = random.choice(list_packs)
            list_packs.remove(choice)
            list_choice.append(choice)
            send_header = struct.pack('3siiiii', b'rnd', choice, num_seq_sender+1, size_data_send, init, end)
            send_packet = send_header + data[choice]
            self.sk.sendto(send_packet, addr)
            recv_packet, addr = self.sk.recvfrom(self.max_pack_legth)
            recv_header = recv_packet[:header_size]
            cmd, pos_pack, num_seq, size_data, init, end = struct.unpack('3siiiii', recv_header)
            if num_seq != num_seq_sender:
                i=i+1
                num_seq_sender = num_seq
            else:
                logging.warn("Pacote n: "+ str(choice) + ' PERDIDO!')
                list_packs.append(choice)
                list_choice.remove(choice)
            recv_data = recv_packet[header_size:]
            song_name = recv_data.decode()
        send_header = struct.pack('3siiiii', b'fin', pos_pack, num_seq+1, size_data, 0, 0)
        data_send = struct.pack('i', 0)
        send_packet = send_header + data_send
        self.sk.sendto(send_packet, addr)
        logging.info('Arquivo enviado')
        print('Final: ', i, ' ', size_data_send*(i-1), ' ', end)

    def seq_random_transmission(self, init, end, cmd, num_seq, data, size_data, addr):
        pass
        
    def normal_transmission(self, init, end, cmd, num_seq, data, size_data, addr):
        header_size = self.parent.header_size
        size_data_send = self.parent.data_size
        i = int(init/size_data_send)
        print(len(data))
        print('size data: ', size_data_send)
        print('Comecanco com: ', i, ' ', i*size_data_send, ' ', init, 'fim: ', end)
        num_pack = end/size_data_send
        print('npack: ', num_pack)
        while i < num_pack:
            pos_pack = i
            send_header = struct.pack('3siiiii', cmd, pos_pack, num_seq+1, size_data_send, init, end)
            time.sleep(0.02)
            send_packet = send_header + data[i]
            self.sk.sendto(send_packet, addr)
            i=i+1
            recv_packet, addr = self.sk.recvfrom(self.max_pack_legth)
            recv_header = recv_packet[:header_size]
            cmd, pos_pack, num_seq, size_data, init, end = struct.unpack('3siiiii', recv_header)
            recv_data = recv_packet[header_size:]
            song_name = recv_data.decode()
        print('Final: ', i, ' ', size_data_send*(i-1), ' ', end)

    def send_file(self, cmd, addr, recv_packet):
        
        self.parent.header_size = 24
        header_size = self.parent.header_size
        recv_header = recv_packet[:header_size]
        cmd, pos_pack, num_seq, size_data, init, end = struct.unpack('3siiiii', recv_header)
        recv_data = recv_packet[header_size:]
        song_name = recv_data.decode()
        finish = False
        data, num_of_packs, size_data = self.parent.split_files(song_name)        
        print(len(data))
        print(num_of_packs)
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
        logging.info('Thread se comunicanco com: ' + addr[0] + ':' + str(addr[1]))
        self.sk.sendto(data, addr)
        send_header = ''
        send_data = ''

        while True: 

            # data received from client 
            recv_packet, addr = self.sk.recvfrom(self.max_pack_legth) 
            print('Thread servidor recebendo de: ', addr[0], ':', addr[1])

            recv_header = recv_packet[:self.parent.header_size]
            recv_data = recv_packet[self.parent.header_size:]

            cmd, pos_pack, num_seq, size_data, init, end = struct.unpack('3siiiii', recv_header)
            if cmd == b'ext':
                logging.info('Fechando conexao')
                self.sk.close()
                self.parent.quit()
            elif cmd == b'req':
                logging.info('Sendo requisitado')
                has, size_file = self.parent.request_file(recv_data, size_data, addr)
                if has:
                    logging.info('Tenho o arquivo requisitado')
                    num_of_packs = size_file / self.parent.data_size
                    if num_of_packs - int(num_of_packs) > 0:
                        num_of_packs = num_of_packs + 1
                    end = int(num_of_packs)
                    header = struct.pack('3siiiii', b'yes', pos_pack, num_seq+1, size_data, init, end)
                    data_send = struct.pack('i', size_file)
                    send_packet = header + data_send
                    # send back reversed string to client
                    # print('Thread servidor mandando para: ', addr[0], ':', addr[1])
                    #print('Send packet with: ', send_packet.decode())
                    self.sk.sendto(send_packet, addr)
                else:
                    logging.info('Nao tenho o arquivo requisitado')
                    header = struct.pack('3siiiii', b'not', pos_pack, num_seq+1, size_data, init, end)
                    data_send = struct.pack('i', 0)
                    send_packet = header + data_send
                    # send back reversed string to client
                    # print('Thread servidor mandando para: ', addr[0], ':', addr[1])
                    #print('Send packet with: ', send_packet.decode())
                    self.sk.sendto(send_packet, addr)
            elif cmd == b'dow':
                logging.info('Enviando arquivo')
                self.send_file(cmd, addr, recv_packet)
            elif cmd == b'exi':
                logging.info('Fechando conexao')
                self.sk.close()
                self.parent.quit()
            else:
                print('Comando Invalido!')

        # connection closed 

class Seeder():
    def __init__(self, host='127.0.0.1', 
                 port=65000,
                 sharead_path='.',
                 args=None):
        self.max_pack_legth = 160
        self.ext_files = ['wav', 'mp3']
        self.APP_KEY = 'APP_KEY'
        self.header_size = 24
        self.nodes_of_connections = []
        self.R = 0.9
        self.data_size = self.max_pack_legth - self.header_size
        
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
        logging.info('Endereco do seeder: '+ self.addr[0] + ':' + str(self.port))
        self.serv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
        self.serv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serv_socket.bind(('', port))

    def get_files_for_share(self):
        caminhos = [os.path.join(self.sharead_path, nome) for nome in os.listdir(self.sharead_path)]
        arquivos = [arq.split('\\')[-1].replace('./', '') for arq in caminhos if os.path.isfile(arq)]
        print(arquivos)
        return arquivos

    def get_only_music_files(self):
        files = self.get_files_for_share()
        return [ music_file for music_file in files if music_file.split('.')[-1] in self.ext_files ]

    def get_my_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))

        data_addr = s.getsockname()
        logging.info('Endereco local do seeder: '+ data_addr[0])
        s.close()
        return data_addr[0]

    def split_files(self, name_file):
        #retorna o tamanho em bytes
        size = os.path.getsize(name_file)
        data_vector = []
        num_of_packs = size/self.data_size
        if num_of_packs - int(num_of_packs) > 0:
            num_of_packs = num_of_packs + 1
        num_of_packs = int(num_of_packs)
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
            logging.info('Conexao com o leecher numero: ' + str(self.connect_count) + ' no endereco: ' + str(addr[0]) + ':' + str(addr[1]))
            # Start a new thread and return its identifier 
            if packet.decode() == self.APP_KEY:
                num = random.randint(49152, 65534)
                n = NodeServer(self, ("", num))
                logging.info('Atendendo o leecher numero: ' + str(self.connect_count) + ' no endereco: ' + str(n.addr[0]) + ':' + str(n.addr[1]))
                self.nodes_of_connections.append(n)
                start_new_thread(n.thread_server, (addr, packet)) 
        self.serv_socket.close()
    
    def request_file(self, name, size_data, addr):
        song_name = name.decode()
        if song_name in self.get_only_music_files():
            file_stats = os.stat(os.path.join(self.sharead_path, song_name))
            return True, file_stats[stat.ST_SIZE]
        else:
            return False, None

    def quit(self):
        logging.info('Fechando servidor')
        self.serv_socket.close()
        exit()

def setup_logging():
    format = "%(asctime)s: '%(name)s - %(levelname)s - %(message)s'"
    logging.basicConfig(filename='seeder.log',
                        format=format, 
                        level=logging.INFO,
                        datefmt="%m/%d %H:%M:%S")
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(asctime)s: %(name)-12s - %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

if __name__ == "__main__":

    setup_logging()

    parser = argparse.ArgumentParser(description="testing btpeer.py")
    parser.add_argument("--port", type=int)
    parser.add_argument("--host", type=str)
    parser.add_argument("--path", type=str)
    args = parser.parse_args()

    logging.info('Iniciando servicos do seeder')
    server = Seeder(args=args)
    # server.get_files_for_share()
    server.run_server()
    
    exit()
