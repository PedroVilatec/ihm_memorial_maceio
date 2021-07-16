import os
import json
import time
cliente = "krause"
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Config():
	def __init__(self):
		self.json_config = {}
		try:
			with open(os.path.join(ROOT_DIR, "config", "config_cerimonia.json"), encoding='utf-8') as json_file:
				self.json_config = json.load(json_file)
				#print(json.dumps(self.json_config , indent=4, ensure_ascii=False))
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
			"VIDEO_FILES":[ "*.mp4", "*.mkv", "*.avi", "*.wmv", "*.mpeg", "*.flv", "*.mov"],
			"AUDIO_FILES":["*.mp3", "*.wav", "*.ogg", "*.aac", "*.aiff", "*.pcm", "*.flac", "*.wma"],
			"TOPICO_INT_IHM": "capela/ihm",
			"TOPICO_EXT_IHM": "capela/{}/ihm".format(cliente),
			"PORTA_MQTT": 1883,
			'AUDIO_IHM':False,
			'CEMITERIO':'krause',
			'TOPICO_IN_SERVER':'capela/cerimonia',
			'TOPICO_EXT_SERVER':'capela/{}/cerimonia'.format(cliente),
			'VIDEO_EXTERNO':{
				'ENABLE':True,
				"VOLUME":1,
				'URL': "Feminino.mp4"},
			'VIDEO_LOCAL':{
				'PULSA_VERMELHO':False,
				"VOLUME":1,
				'INIC_CH_PETALAS':218,
				'ACENDE_CENARIO':365,
				'INIC_PULSA_CRUZ':339,
				'FIM_PULSA_CRUZ':352,
				'INIC_SEQUENCIA':213,
				'INIC_FUMACA':208,
				'APAGA_CRUZ':360,
				# 'URL':os.path.join(os.getcwd(),"CAPELA", "cerimonia", "videos", "video_1.mp4")},
				'URL':"Flores e cachoeiras.mp4"},
			'IHM_AUDIO':{
				'INDEX':None,
				'NAME':None,
				'VOLUME':50}}}

		with open(os.path.join(ROOT_DIR, "config", "config_cerimonia.json"), 'w') as outfile:
			outfile.write(json.dumps(self.json_config , ensure_ascii=False, indent=4))

	def reset_cenario(self):
		config = {}
		os.system('rm '+ os.path.join(ROOT_DIR, "config", "config_cerimonia.json"))
		self.cria_config()
		with open(os.path.join(ROOT_DIR, "config", "config_cerimonia.json"), encoding='utf-8') as json_file:
			config = json.load(json_file)
		return config

	def salva_config(self, data):
		with open(os.path.join(ROOT_DIR, "config", "config_cerimonia.json"), 'w') as outfile:
			outfile.write(json.dumps(data , indent=4, ensure_ascii=False))
