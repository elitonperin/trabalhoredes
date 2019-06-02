# Import socket module 
import socket 

# import thread module 
from _thread import *
import threading 

#import utils module
import random
import time
import struct
import numpy
import logging
from datetime import datetime

#import audio module
# import pyaudio
# from pydub import AudioSegment

class SeederInfo():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.addr = (ip, port)
        self.list_of_musics = []

class NodeServer():
    def __init__(self, parent, addr=None):
        self.init = None
        self.end = None
        self.parent = parent
        self.max_pack_legth = 1280
        self.addr = addr
        self.download_req = False
        self.search_song_op = False
        self.has_song = False
        self.init = 0
        self.end = 0
        self.sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sk.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
        self.sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.event = threading.Event()

        if addr is not None:
            self.sk.bind(self.addr)
        else:
            self.sk.bind(('', 0))
            self.addr = self.sk.getsockname()
        self.port = self.addr[1]
        self.ip = self.addr[0]
        logging.info('Criando socket UDP com IP:PORT: '+str(self.addr[0]) + str(self.addr[1]))

    def header_request(self, num_seq, size_data):
        pos_pack = init = end = 0
        header = struct.pack('3siiiii', b'req', pos_pack, num_seq, size_data, init, end)
        return header

    def header_download(self, pos_pack, num_seq, size_data, init, end):
        header = struct.pack('3siiiii', b'dow', pos_pack, num_seq, size_data, init, end)
        return header

    def download(self, num_seq, song_name, addr):
        data_ = []
        header_size = 24
        pos_pack = -1
        send_header = self.header_download(num_seq+1, pos_pack, len(song_name), int(self.init), int(self.end))
        send_data = song_name.encode()
        send_packet = send_header + send_data
        # print('Thread cliente mandando para: ', addr[0], ':', addr[1])
        self.sk.sendto(send_packet, addr)

        # data received from client
        recv_packet, addr = self.sk.recvfrom(self.max_pack_legth)
        # print('Thread cliente recebendo de: ', addr[0], ':', addr[1])
        recv_header = recv_packet[:header_size]
        # print(recv_header.decode())
        cmd, pos_pack, num_seq, size_data, init, end = struct.unpack('3siiiii', recv_header)
        print(size_data, init, end, num_seq, pos_pack, cmd)
        i = int(self.init/size_data)
        data_.append(recv_packet[header_size:])
        logging.info("Pacote n: " + str(pos_pack) + ' recebido.')

        while i*size_data < self.end:
            send_header = self.header_download(num_seq+1, pos_pack, len(song_name), int(self.init), int(self.end))
            send_data = song_name.encode()
            send_packet = send_header + send_data
            self.sk.sendto(send_packet, addr)
            # data received from client
            recv_packet, addr = self.sk.recvfrom(self.max_pack_legth)
            recv_header = recv_packet[:header_size]
            cmd, pos_pack, num_seq, size_data, init, end = struct.unpack('3siiiii', recv_header)
            logging.info("Pacote n: " + str(pos_pack) + ' recebido.')
            if cmd != b'fin':
                recv_data = recv_packet[header_size:]
                data_.append(recv_data)
            else:
                i = self.end + 1
        data = b''.join(data_)
        logging.info('Quantidade de dados de pacotes recebidos: ' + str(len(data)))

        return num_seq, data

    def thread_client(self, event, data, addr):
        self.on = True
        num_seq = 0
        while self.on:
            event.wait()
            self.event.clear()
            if self.download_req:
                logging.info('Fazendo download da musica: ' + self.parent.song_to_search)
                num_seq, data = self.download(num_seq, self.parent.song_to_search, addr)
                self.data = data
                self.event.set()
                time.sleep(0.3)
                num_seq += 1
            elif self.search_song_op:
                logging.info('Buscando musica: ' + self.parent.song_to_search + ' no seeder com IP: ' + str(addr[0]) + ':' + str(addr[1]))
                header = self.header_request(num_seq+1, len(self.parent.song_to_search))
                data = self.parent.song_to_search.encode()
                send_packet = header + data
                self.sk.sendto(send_packet, addr)

                # data received from client
                recv_packet, addr = self.sk.recvfrom(self.max_pack_legth)
                recv_header = recv_packet[:self.parent.header_size]
                cmd, pos_pack, num_seq, size_data, init, end = struct.unpack('3siiiii', recv_header)
                data = struct.unpack('i', recv_packet[self.parent.header_size:])
                self.size_file = data[0]
                self.init = init
                self.end = end
                self.event.set()
                time.sleep(0.3)
            else:
                print('Nada')
        self.sk.close()

class Leecher():
    def __init__(self, args=None):
        self.ip_broadcast = self.my_mask_for_broadcast()
        self.max_pack_length = 1280
        self.list_seeders = []
        self.APP_KEY = 'APP_KEY'
        self.on = True
        self.list_threads = []
        self.event = threading.Event()
        self.header_size = 24

        self.cli_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.cli_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.cli_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # self.setup_player()
        pass

    '''
        Busca a mascara numa rede classe C de acordo com o endereco de rede
        de rede classe C
    '''
    def my_mask_for_broadcast(self):
        my_ip = self.get_my_local_ip()
        my_ip = my_ip.split('.')
        my_ip[-1] = '255'
        my_ip = '.'.join(my_ip)
        return my_ip

    def get_my_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        data_addr = s.getsockname()
        logging.info('IP Local do leecher: ' + data_addr[0] + ":"+ str(data_addr[1]))
        s.close()
        return data_addr[0]

    def quit(self):
        for soc in self.list_threads:
            soc.on = False
            soc.sk.close()
        self.cli_socket.close()
        exit()

    def listen(self):
        n_con = 0
        running = True
        while running:
            packet, addr = self.cli_socket.recvfrom(self.max_pack_length)
            n_con += 1
            s = SeederInfo(addr[0], addr[1])
            self.list_seeders.append(s)
            logging.info('Conexao com seeder de numero: ' + str(n_con))
            num = random.randint(49152, 65534)
            n = NodeServer(self, ("", num))
            logging.info('Atendendo seeder: ' + str(n_con) + ' na porta: ' + str(num))
            self.list_threads.append(n)
            start_new_thread(n.thread_client, (self.event, packet, addr))

    def setup_player(self):
        self.chunk = 1024
        # song = AudioSegment.from_mp3("never_gonna_give_you_up.mp3", format)
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 64000

        self.player = pyaudio.PyAudio()

        self.stream = self.player.open(format = FORMAT,
                        channels = CHANNELS,
                        rate = RATE,
                        output = True)

    def finish(self):
        self.stream.stop_stream()
        self.stream.close()
        self.player.terminate()

    def play_audio(self, data):

        for i in range(0, len(data), self.chunk):
            self.stream.write(data[i:i+self.chunk])

    def request_file(self):
        self.cli_socket.sendto("cello.wav".encode(), self.list_seeders[0].addr)
        print('Solicitacao enviada')
        msg, addr = self.cli_socket.recvfrom(self.max_pack_length)

        num_of_packs, size, data_size = struct.unpack('fii', msg)
        print(num_of_packs, size, data_size)
        i = 0
        size_to_play = 510
        data = []

        while i < num_of_packs:
            msg, addr = self.cli_socket.recvfrom(data_size)
            data.append(msg)
            i=i+1
            if i%size_to_play == 0:
                sound = data[i-size_to_play:i]
                sound = b''.join(sound)
                self.play_audio(sound)

        data = b''.join(data)
        f = open("novo.wav", "w+b")
        f.write(data)
        f.close()

    def modulo_losts(self):
        numpy.random.exponential()
        pass

    def run_client(self):
        msg = input("digite uma mensagem para enviar ao servidor: ")
        self.cli_socket.sendto(msg.encode(), self.list_seeders[0].addr)
        print ('mensagem enviada' )
        packet, addr = self.cli_socket.recvfrom(self.max_pack_length)
        print('Mensagem recebida: ', packet.decode())
        self.cli_socket.close()

    def do_download(self, size_data, n_seeders):
        part = self.end/n_seeders
        print('Tamanho da parte: ', part)
        i = 0
        for n in self.list_threads:
            n.search_song_op = False
            if n.has_song:
                n.init = int(part)*i
                n.end = int(part)*(i+1)
                print('seeder: ', i)
                print("Comeco: ", n.init, " Fim: ", n.end)
            i += 1
        if part - int(part) > 0:
            self.list_threads[-1].end += 1

        self.event.set()
        time.sleep(0.5)
        for n in self.list_threads:
            if n.has_song:
                n.event.wait()
        self.event.clear()
        data = b''
        for n in self.list_threads:
            data = data + n.data

        f = open(str(datetime.now().hour) + "-novo-"+ str(datetime.now().minute) + ".wav", "w+b")
        f.write(data)
        f.close()
        pass

    def search_song(self, song_name):
        self.song_to_search = song_name
        for n in self.list_threads:
            n.search_song_op = True
        self.event.set()
        print('Esperando...')
        for n in self.list_threads:
            n.event.wait()
        self.event.clear()
        print('Feito')
        count = 0
        for n in self.list_threads:
            if n.size_file > 0:
                n.has_song = True
                info = n.size_file
                self.end = n.end
                self.init = n.init
                count+=1
            else:
                n.has_song = False

        if count == 0:
            return False, count, ''
        else:
            return True, count, info

    def broadcast(self, port=65000):
        # mensagem com codigo para encontrar aplicacao
        self.cli_socket.sendto(self.APP_KEY.encode(),
                    (self.ip_broadcast, port))
        logging.info('Endereco de Broadcast: ' + self.ip_broadcast)
        logging.info('Broadcast enviado na porta: ' + str(port))
        ip, port = self.cli_socket.getsockname()
        logging.info("Meu endereco e: " + ip + ":" + str(port))

        # thread para escutar devolucoes desse broadcast
        start_new_thread(self.listen, ())

    def main(self):
        # broadcast na rede para encontrar os seeders
        # a porta eh configuravel para o broadcast
        running = True

        self.broadcast()
        # menu de opcoes
        while running:
            # ask the client whether he wants to continue
            ans = input('\nO que vc quer :\n1-Buscar musica\n2 - sair\n')
            if ans == '1':
                song_name = input('\nDigita nome:\n')
                time.sleep(0.5)
                s_ans, count, info = self.search_song(song_name)
                if s_ans:
                    print('Arquivo encontrado em ', count, 'peers')
                    print('Informacoes: ', info)
                    ans_d = input('Deseja fazer o download: (y/n) \n')
                    if ans_d.lower() == 'y':
                        for n in self.list_threads:
                            if n.has_song:
                                n.download_req = True
                        self.do_download(info, count)
                else:
                    print('Arquivo nao encontrado')
            elif ans == '2':
                self.quit()
            else:
                print('Comando Invalido')
            print(self.list_seeders)
        print(self.list_threads)

def setup_logging():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(filename='leecher.log',
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

if __name__ == '__main__':

    setup_logging()

    logging.info('Iniciando servicos do leecher')
    leecher = Leecher()
    leecher.main()
