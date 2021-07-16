#encoding: utf-8
#!/usr/bin/env python3.5
#import smbus
from fnmatch import fnmatch
from operations.mqtt import MosquittoServer, Mosquitto
import config #configurações dos controladores rgb
import linecache
import time
import threading

import signal
import serial
import serial.tools.list_ports
global serial_data
import json
from omxplayer.player import OMXPlayer
from instance.config import Config
#from operations.telegram import Bot
from pathlib import Path
from time import sleep
import logging
import subprocess
import datetime
import os
import filecmp
import sys
import termios, tty
TOPICO = "capela/crato"
from check_internet import have_internet
volume = 1
root = os.path.dirname(os.path.abspath(__file__))
pattern = "*.py"
inicio_chuva_petalas = 218
acende_scenario = 365
inicio_pulsa_cruz = 340
fim_pulsa_cruz = 350
inicio_sequencia = inicio_chuva_petalas - 5
inicio_fumaca = inicio_chuva_petalas - 5 - 5
for path, subdirs, files in os.walk(root):
	for name in files:
		if fnmatch(name, pattern):
			if not ".debris" in path:
				try:
					#os.system("rm " + os.path.join(path, name+"_")) #remover todos
					if not(filecmp.cmp (os.path.join(path, name) ,os.path.join(path, "."+name+"_"))):
						os.system("sudo cp " + os.path.join(path, name)+" "+os.path.join(path, "." + name + "_"))

				except Exception as e:
					os.system("sudo cp " + os.path.join(path, name)+" "+os.path.join(path, "." + name + "_"))
					print("Novo arquivo criado: ",os.path.join(path, name))

def printException():
	exc_type, exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def buttonPressed(status):
	'''ATRIBUI A CERIMONIA AO BOTAO PRESSIONADO NO PAINEL'''
	global CONFIGURACAO
	global videoDuration

	if status == 1:
		CONFIGURACAO = config.CERIMONIA_1
		try:
			player.load(config.video_1,  pause=False)
			time.sleep(1)
			player.pause()
			player.set_aspect_mode('stretch')

			#player.set_video_pos(200, 0, 680, 480)
			print(player.video_pos())
		except Exception as ex:
			print(ex)

	if status == 2:
		CONFIGURACAO = config.CERIMONIA_2
		print(CONFIGURACAO)
		try:
			player.load(config.video_2,  pause=False)
			time.sleep(1)
			player.pause()
			player.set_aspect_mode('stretch')
		except Exception as ex:
			print(ex)

	if status == 3:
		CONFIGURACAO = config.CERIMONIA_3
		print(CONFIGURACAO)
		try:
			player.load(config.video_3,  pause=False)
			time.sleep(1)
			player.pause()
			player.set_aspect_mode('stretch')
		except Exception as ex:
			print(ex)

	if status == 4:
		CONFIGURACAO = config.CERIMONIA_4
		print(CONFIGURACAO)
		try:
			player.load(config.video_4,  pause=False)
			time.sleep(1)
			#player.pause()
			player.set_aspect_mode('stretch')
		except Exception as ex:
			print(ex)


	if status == 5:
		CONFIGURACAO = config.CERIMONIA_5
		print(CONFIGURACAO)
		try:
			player.load(config.video_5,  pause=False)
			time.sleep(1)
			player.pause()
			player.set_aspect_mode('stretch')
		except Exception as ex:
			print(ex)

	videoDuration = player.duration()
	#~ while player.playback_status() != "Paused":
		#~ player.pause()
		#~ time.sleep(.01)
	time.sleep(.1)
	#~ tempo = time.time()
	player.set_volume(volume)
	print("Volume " + str(player.volume()))
	print("O vídeo %d tem %.2f segundos de duração "%(status, player.duration()))

def process_serial(dados):
	if dados != "":
		global CONFIGURACAO
		print("Dados serial " +str(dados))
		global tempo
		global intervalo
		global lastIntervalo
	
		if dados == 'GUARDAMESA':
			print("player position", player.position())
			pass
	
		if dados == 'ABRINDO A PORTA':
			# ~ print("Player position abre", player.position())
			pass
	
		if dados == 'FECHA PORTA':
			'''ACENDE A CAPELA APÓS O TEMPO config.ACENDE_SCENARIO'''
			print("Player position inicio fechamento", player.position())
			pass		
	
		if dados == 'PORTA FECHADA':
			'''ACENDE A CAPELA APÓS O TEMPO config.ACENDE_SCENARIO'''
			print("Player position final fechamento", player.position())
			pass
	
		if dados == 'TIME':
			print(tempo - time.time())
			tempo = time.time()
			pass
		if dados == 'APAGA_CABINE':
			#~ J2=Job('change', "SANCA_CABINE", ' -C gradual 90 "(0,0,0)"')
			#~ J2.start()
	
			pass
		if dados != 'ONLINE':
			pass
			
		if dados == 'button_counter = 2':
			serial_mega.write(b'GPIO,42,1\n')		
			
		if dados == 'ESTEIRA DESLIGADA':
			serial_mega.write(b'LED_ESTEIRA,0\n')
	
		if dados == 'CERIMONIA_COMPLETA':
			# ~ try:
				# ~ telegram_bot.envia_telegram_single("334240998", "CERIMONIA INICIADA")
			# ~ except:
				# ~ print("ERRO TELEGRAM")
			global iniciada
			iniciada = True
			passedScenario1 = False
			passedScenario2 = False
			serial_mega.write(b'COMPLETA\n')
			serial_mega.write(b'<0,0,0,0,0,8,0,0,0,0>\n')
			time.sleep(.1)
	
			cmd = {"display_off":"display_off"}
			cmd = json.dumps(cmd)
			mqttLocal.mqttc.publish("capela/ihm", cmd, qos=2)
			serial_mega.write(b'B_C\n')
			# ~ for a in range(22):
				# ~ print("aguardando", 22 - a, "segundos", end = "\r")
				# ~ time.sleep(1)
	
			#time.sleep(25) #delay da cortina
	
			#
			player.set_position(1.)
			
			# ~ player.set_position(200)
			# ~ player.seek(280)
			player.play()
			#player.load(source, pause=False)
	
		
class Liga_manual (threading.Thread):
##  '''VERIFICAR SE A THREAD RODA SEM O PCF8574 INSTALADO'''
	def __init__(self):
		threading.Thread.__init__(self)
		# The shutdown_flag is a threading.Event object that
		# indicates whether the thread should be terminated.
		self.shutdown_flag = threading.Event()

	def run(self):
		serial_mega.write(b'DIMER,1,100\n')
		time.sleep(2)
		serial_mega.write(b'DIMER,2,100\n')
		time.sleep(2)		
		serial_mega.write(b'DIMER,3,100\n')
		time.sleep(2)
		serial_mega.write(b'DIMER,4,100\n')
		time.sleep(2)
		serial_mega.write(b'DIMER,5,100\n')
		time.sleep(2)
		serial_mega.write(b'DIMER,6,100\n')
		time.sleep(2)
		serial_mega.write(b'DIMER,8,100\n')
		time.sleep(2)
		serial_mega.write(b'DIMER,9,100\n')
		time.sleep(2)
		serial_mega.write(b'DIMER,10,100\n')
		time.sleep(2)
		serial_mega.write(b'GPIO,42,0\n')
		time.sleep(10)
		serial_mega.write(b'T_DIM,50\n')

class readSerial(threading.Thread):
##  '''VERIFICAR SE A THREAD RODA SEM O PCF8574 INSTALADO'''
	def __init__(self):
		threading.Thread.__init__(self)
		# The shutdown_flag is a threading.Event object that
		# indicates whether the thread should be terminated.
		self.shutdown_flag = threading.Event()

	def run(self):
			#liga_todos()
			while not self.shutdown_flag.is_set():
				try:
					global serial_mega
					if serial_mega.isOpen():
						reading = serial_mega.readline().decode("utf-8").rstrip()
						process_serial(reading)

				except:
					pass

class ServiceExit(Exception):
	"""
	Custom exception which is used to trigger the clean exit
	of all running threads and the main program.
	"""
	pass


def service_shutdown(signum, frame):
	print('Caught signal %d' % signum)
	raise ServiceExit


def main():
	global iniciada
	global videoDuration
	global intervalo
	global lastIntervalo
	global CONFIGURACAO
	global passedScenario1
	global passedScenario2
	# Register the signal handlers
	signal.signal(signal.SIGTERM, service_shutdown)
	signal.signal(signal.SIGINT, service_shutdown)

	print('Starting main program')

	# Start the job threads
	buttonPressed(1)
	try:


		pass
		time_video = player.position()
		ler_serial = readSerial()
		ler_serial.start()

		looping = time.time()
		lastLooping = time.time()
		time_cortinas = time.time()

		while True:
			if mqttLocal.desligar == True:
				time.sleep(2)
				os.system("sudo poweroff")

			if player.playback_status() == "Playing" and looping < time.time():
				time_video = player.position()
				looping = time.time() + .5

				if time_video >= inicio_fumaca and time_video <= inicio_fumaca + 1:
					serial_mega.write(b'fum,12000\n')


				if time_video >= inicio_chuva_petalas and time_video <= inicio_chuva_petalas +1:
					print("chuva_petalas")
					serial_mega.write(b'CHUVAPETALAS,128\n')
					serial_mega.write(b'LED_ESTEIRA,255\n')
					#serial_mega.write(b'<0,0,0,0,0,100,0,0,0,100>\n')

				if time_video >= inicio_sequencia and time_video <= inicio_sequencia + 1:
					print(" sequencia")
					serial_mega.write(b'sequencia\n')
					time.sleep(1)
					serial_mega.write(b'LED_CABINE,255,255,0\n')


				if time_video >= inicio_pulsa_cruz and time_video <= inicio_pulsa_cruz + 1:
					print("pulsa cruz")
					serial_mega.write(b'EN_RGB_GERAL,1\n')# habilita o loop pulsante vermelho
					time.sleep(1)
					serial_mega.write(b'[100,0,0,100,0,0,5,0,0,5,0,0]\n')

				if time_video >= fim_pulsa_cruz and time_video <= fim_pulsa_cruz + 1:
					print(" desabilita pulsa cruz")
					serial_mega.write(b'EN_RGB_GERAL,0\n')
					time.sleep(1)
					serial_mega.write(b'(0,0,0,0,0,0,0,0,0)\n')

				if time_video >= acende_scenario and time_video <= acende_scenario + 1:
					print(" fim de cerimonia")
					serial_mega.write(b'S_C\n')
					serial_mega.write(b'T_DIM,100\n')
					# ~ serial_mega.write(b'<100,100,100,100,100,100,100,100,100,100>\n')#luz no fim da cerimonia
					time.sleep(1)
					serial_mega.write(b'(255,255,255,0,0,0,255,255,255)\n')
					iluminacao_manual = Liga_manual()
					iluminacao_manual.start()					

				print(time_video, end = '\r')


			if player.can_control() and time_video > videoDuration - 2:
				while player.playback_status() != "Paused":
					print("pausando video")
					player.pause()
					

				#videoDuration = player.duration()
				time.sleep(.5)

				iniciada = False



	except ServiceExit:
		pass
		# Terminate the running threads.
		# Set the shutdown flag on each thread to trigger a clean shutdown of each thread.
##        j1.shutdown_flag.set()

		# Wait for the threads to close...
##        j1.join()


	print('Exiting main program')


	


try:
	os.system("sudo killall omxplayer.bin")
except:
	pass

logging.basicConfig(level=logging.INFO)

source = "/usr/share/APP/videos/video_1.mp4"
try:
	player_log = logging.getLogger("Player 1")
	player = OMXPlayer(source, args=[  '-o', 'local', '--no-osd','-b'], dbus_name='org.mpris.MediaPlayer2.omxplayer1')
	player.set_aspect_mode('stretch')
except:# NameError:# dbus.exceptions.DBusException:
	print("Reiniciando App")
	os.execv(sys.executable, ['python3'] + sys.argv)
else:
	print("Exception")


#~ player.set_aspect_mode('fill')

#time.sleep(20)
while player.playback_status() != "Paused":
	player.pause()
tempo = time.time()
print("video pausado")
player.set_volume(volume)
#player.mute()
print("Player mute")
print("Volume " + str(player.volume()))
print("O vídeo tem %.2f segundos de duração "%player.duration())

serial_mega = None
serial_nano = None

def config_serial():
	global serial_mega
	global serial_nano
	print("function")
	lista_porta=[]
	portas_abertas=[]
	ports = serial.tools.list_ports.comports()
	
	for port, desc, hwid in sorted(ports):
	        if "USB" in port:
	            lista_porta.append(port)
	
	for portas in lista_porta:
		'''
		Abre todas as portas
		'''
		try:
			portas_abertas.append(serial.Serial(portas, 9600, timeout=1))
		except:
			print(portas, "Acesso negado")
	
	try:
		
		while serial_mega == None or serial_nano == None:
			for channel in portas_abertas:
				if channel != serial_mega and channel != serial_nano:
					channel.write(b'MODEL\n')
					time.sleep(.1)
					string = channel.readline().decode("utf-8", "ignore")
					if serial_nano == None:
						if "NANO" in string:
							#print("Porta NANO", lista_porta[portas_abertas.index(channel)])
							serial_nano = channel
					if serial_mega == None:
						if "MEGA" in string:
							#print("Porta MEGA", lista_porta[portas_abertas.index(channel)])
							serial_mega = channel
		print("Porta serial MEGA = {}\nPorta serial NANO = {}".format(lista_porta[portas_abertas.index(serial_mega)], lista_porta[portas_abertas.index(serial_nano)]))
		mqttServer.serial_nano = serial_nano
		mqttServer.serial_mega = serial_mega
		mqttLocal.serial_nano = serial_nano
		mqttLocal.serial_mega = serial_mega		
	except Exception as e:
		print(e)
		print("Porta Serial não aberta")
		
thread = threading.Thread(target=config_serial)
thread.start()			
mqttLocal = Mosquitto(TOPICO)
#mqttLocal.player = player
mqttServer = MosquittoServer(TOPICO)
#mqttServer.player = player

if __name__ == '__main__':
	main()


# ~ Traceback (most recent call last):
  # ~ File "video_popen_4_comando_rasp.py", line 430, in <module>
    # ~ main()
  # ~ File "video_popen_4_comando_rasp.py", line 353, in main
    # ~ if player.can_control() and time_video > videoDuration - 2:
  # ~ File "</usr/local/lib/python3.7/dist-packages/decorator.py:decorator-gen-22>", line 2, in can_control
# ~ Dados serial B_C
  # ~ File "/usr/local/lib/python3.7/dist-packages/omxplayer/player.py", line 48, in wrapped
    # ~ return fn(self, *args, **kwargs)
  # ~ File "</usr/local/lib/python3.7/dist-packages/decorator.py:decorator-gen-21>", line 2, in can_control
  # ~ File "/usr/local/lib/python3.7/dist-packages/omxplayer/player.py", line 85, in wrapped
    # ~ return from_dbus_type(fn(self, *args, **kwargs))
  # ~ File "/usr/local/lib/python3.7/dist-packages/omxplayer/player.py", line 342, in can_control
    # ~ return self._player_interface_property('CanControl')
  # ~ File "/usr/local/lib/python3.7/dist-packages/omxplayer/player.py", line 829, in _player_interface_property
    # ~ return self._interface_property(self._player_interface.dbus_interface, prop, val)
  # ~ File "/usr/local/lib/python3.7/dist-packages/omxplayer/player.py", line 823, in _interface_property
    # ~ return self._properties_interface.Get(interface, prop)
  # ~ File "/usr/local/lib/python3.7/dist-packages/dbus/proxies.py", line 147, in __call__
    # ~ **keywords)
  # ~ File "/usr/local/lib/python3.7/dist-packages/dbus/connection.py", line 653, in call_blocking
    # ~ message, timeout)
# ~ dbus.exceptions.DBusException: org.freedesktop.DBus.Error.NoReply: Message recipient disconnected from message bus without replying
# ~ INFO:omxplayer.player:OMXPlayer process is dead, all DBus calls from here will fail

#Player position inicio fechamento 291.791414
#Player position final fechamento 332.850824
