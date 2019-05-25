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

#import audio module
import pyaudio
from pydub import AudioSegment

class SeederInfo():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.addr = (ip, port)
        self.list_of_musics = []

# thread fuction 
class NodeServer():
	def __init__(self, parent, addr=None):
		self.parent = parent
		self.max_pack_legth = 1280
		self.addr = addr
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
	
	def header_request(self, num_seq, size_data):
		header = struct.pack('3sii', b'req', num_seq, size_data)
		return header

	def thread_client(self, data, addr):

		while True: 
			# ask the client whether he wants to continue 
			ans = input('\nO que vc quer :\n1-Buscar musica\n2 - sair\n') 
			if ans == '1':
				song_name = input('\nDigita nome:\n') 
				### busca
				header = self.header_request(1, len(song_name))
				data = song_name.encode()
				send_packet = header + data
				print('Thread cliente mandando para: ', addr[0], ':', addr[1])
				self.sk.sendto(send_packet, addr)

				# data received from client 
				recv_packet, addr = self.sk.recvfrom(self.max_pack_legth) 
				print('Thread cliente recebendo de: ', addr[0], ':', addr[1])
				print(recv_packet.decode())
				print(addr)
				recv_header = recv_packet[:12]
				cmd, num_seq, size_data = struct.unpack('3sii', recv_header)
				if cmd == b'yes':
					ans = input('Deseja baixar:\n (y/n):\n')
					if ans == 'y':
						self.download()
				else:
					print('Nao tem')

				### baixa
			elif ans == '2':
				self.parent.on = False
				self.parent.quit()
				break


        # connection closed 
		self.sk.close()

class Leecher():
	def __init__(self, args=None):
		self.port = 7001
		self.ip_broadcast = self.my_mask_for_broadcast()
		self.max_pack_length = 1280
		self.list_seeders = []
		self.APP_KEY = 'APP_KEY'
		self.on = True
		self.list_threads = []
		
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

	def quit(self):
		for soc in self.list_threads:
			soc.sk.close()
		self.cli_socket.close()
		exit()
	
	def listen(self, nada, nada2):
		n_con = 0
		running = True
		while running:
			packet, addr = self.cli_socket.recvfrom(self.max_pack_length) 
			n_con += 1
			# messaga received from server 
			# print the received message 
			# here it would be a reverse of sent message 
			print('Conexao n:', n_con)
			num = random.randint(49152, 65534)
			n = NodeServer(self, ("", num))
			self.list_threads.append(n)
			start_new_thread(n.thread_client, (packet, addr)) 

	def broadcast(self):
		self.cli_socket.sendto(self.APP_KEY.encode(),
					(self.ip_broadcast, self.port))
		print('Endereco de Boradcast: ', self.ip_broadcast)
		print('Broadcast enviado na porta: ', self.port)
		start_new_thread(self.listen, (None, None)) 
		running = True

		while running:
			# ask the client whether he wants to continue 
			ans = input('\nO que vc quer :\n1-Buscar musica\n2 - sair\n') 
			if ans == '1':
				song_name = input('\nDigita nome:\n') 
			elif ans == '2':
				self.quit()
			else:
				print('Comando Invalido')
			print(self.list_seeders)
			print(self.list_threads)
			

		# while self.on:
		# 	msg, addr = self.cli_socket.recvfrom(self.max_pack_length)
		# 	s = SeederInfo(ip=addr[0], port=addr[1])
		# 	self.list_seeders.append(s)

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

	def main(self): 
		# local host IP '127.0.0.1' 

		# Define the port on which you want to connect 
		# message sent to server 
		# n_seq, init_segm, final_segm, ack, nack, cmd = struct.unpack('iiiiif', packet)
		self.broadcast()
		

if __name__ == '__main__': 
	leecher = Leecher()
	leecher.main()
