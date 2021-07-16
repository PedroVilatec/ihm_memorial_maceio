import os
import json
import time

class Config():
	def __init__(self):
		self.json_config = {}
		try:
			with open('/usr/share/APP/instance/config_cerimonia.txt') as json_file:
				self.json_config = json.load(json_file)
		except:
			self.cria_config()
		
	def cria_config(self):
		self.json_config={}
		# ~ self.json_config = {'CONFIG':{}}
		self.json_config={
		'CONFIG':{
			"TIME":time.time(),
			"TIME_BLOCK_SENHA":60*5, # 5 MINUTOS
			"UPDATE":False,
			"IN_SERVER_IP":None,
			"LOCAL_IP":None,
			"VIDEO_FILES":[ "*.mp4", "*.mkv", "*.avi"],
			"AUDIO_FILES":["*.mp3", "*.wav"],
			"TOPICO_INT_IHM": "capela/ihm",
			"TOPICO_EXT_IHM": "capela/krause/ihm",
			"PORTA_MQTT": 1883,
			'VIDEO_IHM':False,
			'AUDIO_IHM':False,
			'CEMITERIO':'krause',
			'TOPICO_IN_SERVER':'capela/cerimonia',
			'TOPICO_EXT_SERVER':'capela/krause/cerimonia',
			'VIDEO_EXT':{
				'INIC_CH_PETALAS':218,
				'ACENDE_CENARIO':365,
				'INIC_PULSA_CRUZ':340,
				'INIC_SEQUENCIA':213,
				'INIC_FUMACA':208,
				'URL':'/usr/share/APP/videos/video_1.mp4'},
			'VIDEO_1':{
				'INIC_CH_PETALAS':218,
				'ACENDE_CENARIO':365,
				'INIC_PULSA_CRUZ':340,
				'INIC_SEQUENCIA':213,
				'INIC_FUMACA':208,
				'URL':'/usr/share/APP/videos/video_1.mp4'},
			'IHM_AUDIO':{
				'INDEX':None,
				'NAME':None,
				'VOLUME':50}}}

		with open('/usr/share/APP/instance/config_cerimonia.txt', 'w') as outfile:
			# ~ print(json.dumps(self.json_config, indent=2))
			json.dump(self.json_config, outfile)

	def reset_cenario(self):
		config = {}
		try:
			if sys.platform == 'win32':
				os.system("del /usr/share/APP/instance/config_cerimonia.txt")
			else:
				os.system('rm /usr/share/APP/instance/config_cerimonia.txt')
		except:
			pass

		self.cria_config()
		with open('/usr/share/APP/instance/config_cerimonia.txt') as json_file:
			config = json.load(json_file)
		return config

	def salva_config(self, data):
		with open('/usr/share/APP/instance/config_cerimonia.txt', 'w') as outfile:
			outfile.write(json.dumps(data , indent=4))
