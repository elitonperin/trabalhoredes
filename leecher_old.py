import struct
import socket 
import numpy
import pyaudio
from pydub import AudioSegment
import random
from NodeSocket import NodeSocket
from _thread import *
import threading 

def funcao_tocar_mp3():
    from pydub import AudioSegment
    import pyaudio

    p = pyaudio.PyAudio()

    #Open File to get infos from that
    song = AudioSegment.from_file("file.mp3", format="mp3")

    # open stream based on the wave object which has been input.
    stream = p.open(format=p.get_format_from_width(song.sample_width),
                    channels=song.channels,
                    rate=song.frame_rate,
                    output=True)

    fileSize = len(song.raw_data)
    chunkSize = 320

    for piece in range(0, fileSize, chunkSize):
        stream.write(song.raw_data[piece:piece+chunkSize])

    # cleanup stuff.
    stream.stop_stream()
    stream.close()

    p.terminate()


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
        self.ip_broadcast = self.my_mask_for_broadcast()
        self.max_data_length = 1280
        self.list_seeders = []
        self.APP_KEY = 'APP_KEY'
        
        self.cli_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.cli_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.cli_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.setup_player()
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
        print("IP local: ", data_addr[0])
        s.close()
        return data_addr[0]

    def broadcast(self):
        self.cli_socket.sendto(self.APP_KEY.encode(),
                  (self.ip_broadcast, self.port))
        print('Broadcast enviado')
        msg, addr = self.cli_socket.recvfrom(self.max_data_length)
        s = SeederInfo(ip=addr[0], port=addr[1])
        self.list_seeders.append(s)
        return addr

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
            print(i)
            self.stream.write(data[i:i+self.chunk])


    def run_client(self):
        msg = input("digite uma mensagem para enviar ao servidor: ")
        self.cli_socket.sendto(msg.encode(), self.list_seeders[0].addr) 
        print ('mensagem enviada' )
        packet, addr = self.cli_socket.recvfrom(max_data_legth)
        print('Mensagem recebida: ', packet.decode())
        self.cli_socket.close()

    def request_file(self):
        self.cli_socket.sendto("cello.wav".encode(), self.list_seeders[0].addr)
        print('Solicitacao enviada')
        msg, addr = self.cli_socket.recvfrom(self.max_data_length)
        
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

# leecher = Leecher()
# ip, port = leecher.broadcast()
# leecher.run_client()
# leecher.request_file()
# local host IP '127.0.0.1' 
host = '127.0.0.1'

# Define the port on which you want to connect 
port = 7001
addr_send = (host,port)

client = Leecher()

# message sent to server 
n_seq = -1
init_segm = 0
final_segm = 0
ack = 0
nack = 0
cmd = b"new"
data = b'TEXTO'
packet = struct.pack('siiiiis', 
                                cmd,
                                n_seq, 
                                init_segm, 
                                final_segm, 
                                ack,
                                nack,
                                data )
client.cli_socket.sendto(packet, addr_send) 


data, addr = client.cli_socket.recvfrom(client.max_data_length) 
# messaga received from server 
# print the received message 
# here it would be a reverse of sent message 
print('Primeira conexao :', str(data.decode()))
num = random.randint(49152, 65534)
n = NodeSocket(client,("", num))
start_new_thread(n.thread_client, (data, addr)) 
running = True
while running:
    ans = input("Ver rede: ")
    if ans == 'exit':
        running = False